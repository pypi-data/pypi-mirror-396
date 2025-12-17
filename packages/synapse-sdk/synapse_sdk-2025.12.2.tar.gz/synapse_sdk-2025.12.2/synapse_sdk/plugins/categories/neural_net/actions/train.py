import copy
import shutil
import tempfile
from numbers import Number
from pathlib import Path
from typing import Annotated, Callable, Dict, Optional

from pydantic import AfterValidator, BaseModel, field_validator, model_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.models import Run
from synapse_sdk.utils.file import archive, get_temp_path, unarchive
from synapse_sdk.utils.module_loading import import_string
from synapse_sdk.utils.pydantic.validators import non_blank


class TrainRun(Run):
    is_tune = False
    completed_samples = 0
    num_samples = 0
    checkpoint_output = None

    def set_progress(self, current, total, category=''):
        if getattr(self, 'is_tune', False) and category == 'train':
            # Ignore train progress updates in tune mode to keep trials-only bar
            return
        super().set_progress(current, total, category)

    def log_metric(self, category, key, value, **metrics):
        # TODO validate input via plugin config
        data = {'category': category, 'key': key, 'value': value, 'metrics': metrics}

        # Automatically add trial_id when is_tune=True
        if self.is_tune:
            try:
                from ray import train

                context = train.get_context()
                trial_id = context.get_trial_id()
                if trial_id:
                    data['trial_id'] = trial_id
            except Exception:
                # If Ray context is not available, continue without trial_id
                pass

        self.log('metric', data)

    def log_visualization(self, category, group, index, image, **meta):
        # TODO validate input via plugin config
        data = {'category': category, 'group': group, 'index': index, **meta}

        # Automatically add trial_id when is_tune=True
        if self.is_tune:
            try:
                from ray import train

                context = train.get_context()
                trial_id = context.get_trial_id()
                if trial_id:
                    data['trial_id'] = trial_id
            except Exception:
                # If Ray context is not available, continue without trial_id
                pass

        self.log('visualization', data, file=image)

    def log_trials(self, data=None, *, trials=None, base=None, hyperparameters=None, metrics=None, best_trial=''):
        """
        Log structured Ray Tune trial progress tables.

        Args:
            data (dict | None): Pre-built payload to send. Should contain
                ``trials`` (dict) key.
            base (list[str] | None): Column names that belong to the fixed base section.
            trials (dict | None): Mapping of ``trial_id`` -> structured section values.
            hyperparameters (list[str] | None): Column names belonging to hyperparameters.
            metrics (list[str] | None): Column names belonging to metrics.
            best_trial (str): Trial ID of the best trial (empty string during tuning, populated at the end).

        Returns:
            dict: The payload that was logged.
        """
        if data is None:
            data = {
                'base': base or [],
                'trials': trials or {},
                'hyperparameters': hyperparameters or [],
                'metrics': metrics or [],
                'best_trial': best_trial,
            }
        elif not isinstance(data, dict):
            raise ValueError('log_trials expects a dictionary payload')

        if 'trials' not in data:
            raise ValueError('log_trials payload must include "trials" key')

        data.setdefault('base', base or [])
        data.setdefault('hyperparameters', hyperparameters or [])
        data.setdefault('metrics', metrics or [])
        data.setdefault('best_trial', best_trial)

        self.log('trials', data)
        # Keep track of the last snapshot so we can reuse it (e.g., when finalizing best_trial)
        try:
            self._last_trials_payload = copy.deepcopy(data)
        except Exception:
            self._last_trials_payload = data
        return data


class SearchAlgo(BaseModel):
    """
    Configuration for Ray Tune search algorithms.

    Supported algorithms:
        - 'bayesoptsearch': Bayesian optimization using Gaussian Processes
        - 'hyperoptsearch': Tree-structured Parzen Estimator (TPE)
        - 'basicvariantgenerator': Random search (default)

    Attributes:
        name (str): Name of the search algorithm (case-insensitive)
        points_to_evaluate (Optional[dict]): Optional initial hyperparameter
            configurations to evaluate before starting optimization

    Example:
        {
            "name": "hyperoptsearch",
            "points_to_evaluate": [
                {"learning_rate": 0.001, "batch_size": 32}
            ]
        }
    """

    name: str
    points_to_evaluate: Optional[dict] = None


class Scheduler(BaseModel):
    """
    Configuration for Ray Tune schedulers.

    Supported schedulers:
        - 'fifo': First-In-First-Out scheduler (default, runs all trials)
        - 'hyperband': HyperBand early stopping scheduler

    Attributes:
        name (str): Name of the scheduler (case-insensitive)
        options (Optional[str]): Optional scheduler-specific configuration parameters

    Example:
        {
            "name": "hyperband",
            "options": {
                "max_t": 100,
                "reduction_factor": 3
            }
        }
    """

    name: str
    options: Optional[str] = None


class TuneConfig(BaseModel):
    """
    Configuration for Ray Tune hyperparameter optimization.

    Used when is_tune=True to configure the hyperparameter search process.

    Attributes:
        mode (Optional[str]): Optimization mode - 'max' or 'min'
        metric (Optional[str]): Name of the metric to optimize
        num_samples (int): Number of hyperparameter configurations to try (default: 1)
        max_concurrent_trials (Optional[int]): Maximum number of trials to run in parallel
        search_alg (Optional[SearchAlgo]): Search algorithm configuration
        scheduler (Optional[Scheduler]): Trial scheduler configuration

    Example:
        {
            "mode": "max",
            "metric": "accuracy",
            "num_samples": 20,
            "max_concurrent_trials": 4,
            "search_alg": {
                "name": "hyperoptsearch"
            },
            "scheduler": {
                "name": "hyperband",
                "options": {"max_t": 100}
            }
        }
    """

    mode: Optional[str] = None
    metric: Optional[str] = None
    num_samples: int = 1
    max_concurrent_trials: Optional[int] = None
    search_alg: Optional[SearchAlgo] = None
    scheduler: Optional[Scheduler] = None


class TrainParams(BaseModel):
    """
    Parameters for TrainAction supporting both regular training and hyperparameter tuning.

    Attributes:
        name (str): Name for the training/tuning job
        description (str): Description of the job
        checkpoint (int | None): Optional checkpoint ID to resume from
        dataset (int): Dataset ID to use for training
        is_tune (bool): Enable hyperparameter tuning mode (default: False)
        tune_config (Optional[TuneConfig]): Tune configuration (required when is_tune=True)
        num_cpus (Optional[int]): CPUs per trial (tuning mode only)
        num_gpus (Optional[int]): GPUs per trial (tuning mode only)
        hyperparameter (Optional[Any]): Fixed hyperparameters (required when is_tune=False)
        hyperparameters (Optional[list]): Hyperparameter search space (required when is_tune=True)

    Hyperparameter format when is_tune=True:
        Each item in hyperparameters list must have:
        - 'name': Parameter name (string)
        - 'type': Distribution type (string)
        - Type-specific parameters:
            - uniform/quniform: 'min', 'max'
            - loguniform/qloguniform: 'min', 'max', 'base'
            - randn/qrandn: 'mean', 'sd'
            - randint/qrandint: 'min', 'max'
            - lograndint/qlograndint: 'min', 'max', 'base'
            - choice/grid_search: 'options'

    Example (Training mode):
        {
            "name": "my_training",
            "dataset": 123,
            "is_tune": false,
            "hyperparameter": {
                "epochs": 100,
                "batch_size": 32,
                "learning_rate": 0.001
            }
        }

    Example (Tuning mode):
        {
            "name": "my_tuning",
            "dataset": 123,
            "is_tune": true,
            "hyperparameters": [
                {"name": "batch_size", "type": "choice", "options": [16, 32, 64]},
                {"name": "learning_rate", "type": "loguniform", "min": 0.0001, "max": 0.01, "base": 10},
                {"name": "epochs", "type": "randint", "min": 5, "max": 15}
            ],
            "tune_config": {
                "mode": "max",
                "metric": "accuracy",
                "num_samples": 10
            }
        }
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str
    checkpoint: int | None
    dataset: int
    is_tune: bool = False
    tune_config: Optional[TuneConfig] = None
    num_cpus: Optional[int] = None
    num_gpus: Optional[int] = None
    hyperparameter: Optional[dict] = None  # plan to be deprecated
    hyperparameters: Optional[list] = None

    @field_validator('hyperparameter', mode='before')
    @classmethod
    def validate_hyperparameter(cls, v, info):
        """Validate hyperparameter for train mode (is_tune=False)"""
        # Get is_tune flag to determine if this field should be validated
        is_tune = info.data.get('is_tune', False)

        # If is_tune=True, hyperparameter should be None/not used
        # Just return whatever was passed (will be validated in model_validator)
        if is_tune:
            return v

        # For train mode, hyperparameter should be a dict
        if isinstance(v, dict):
            return v
        elif isinstance(v, list):
            raise ValueError(
                'hyperparameter must be a dict, not a list. '
                'If you want to use hyperparameter tuning, '
                'set "is_tune": true and use "hyperparameters" instead.'
            )
        else:
            raise ValueError('hyperparameter must be a dict')

    @field_validator('hyperparameters', mode='before')
    @classmethod
    def validate_hyperparameters(cls, v, info):
        """Validate hyperparameters for tune mode (is_tune=True)"""
        # Get is_tune flag to determine if this field should be validated
        is_tune = info.data.get('is_tune', False)

        # If is_tune=False, hyperparameters should be None/not used
        # Just return whatever was passed (will be validated in model_validator)
        if not is_tune:
            return v

        # For tune mode, hyperparameters should be a list
        if isinstance(v, list):
            return v
        elif isinstance(v, dict):
            raise ValueError(
                'hyperparameters must be a list, not a dict. '
                'If you want to use fixed hyperparameters for training, '
                'set "is_tune": false and use "hyperparameter" instead.'
            )
        else:
            raise ValueError('hyperparameters must be a list')

    @field_validator('name')
    @staticmethod
    def unique_name(value, info):
        action = info.context['action']
        client = action.client
        is_tune = info.data.get('is_tune', False)
        encoded_value = value.replace(':', '%3A').replace(',', '%2C')
        try:
            if not is_tune:
                model_exists = client.exists('list_models', params={'name': value})
                job_exists = client.exists(
                    'list_jobs',
                    params={
                        'ids_ex': action.job_id,
                        'category': 'neural_net',
                        'job__action': 'train',
                        'is_active': True,
                        'params': f'name:{encoded_value}',
                    },
                )
                assert not model_exists and not job_exists, '존재하는 학습 이름입니다.'
            else:
                job_exists = client.exists(
                    'list_jobs',
                    params={
                        'ids_ex': action.job_id,
                        'category': 'neural_net',
                        'job__action': 'train',
                        'is_active': True,
                        'params': f'name:{encoded_value}',
                    },
                )
                assert not job_exists, '존재하는 튜닝 작업 이름입니다.'
        except ClientError:
            raise PydanticCustomError('client_error', '')
        return value

    @model_validator(mode='after')
    def validate_tune_params(self):
        if self.is_tune:
            # When is_tune=True, hyperparameters is required
            if self.hyperparameters is None:
                raise ValueError('hyperparameters is required when is_tune=True')
            if self.hyperparameter is not None:
                raise ValueError('hyperparameter should not be provided when is_tune=True, use hyperparameters instead')
            if self.tune_config is None:
                raise ValueError('tune_config is required when is_tune=True')
        else:
            # When is_tune=False, either hyperparameter or hyperparameters is required
            if self.hyperparameter is None and self.hyperparameters is None:
                raise ValueError('Either hyperparameter or hyperparameters is required when is_tune=False')

            if self.hyperparameter is not None and self.hyperparameters is not None:
                raise ValueError('Provide either hyperparameter or hyperparameters, but not both')

            if self.hyperparameters is not None:
                if not isinstance(self.hyperparameters, list) or len(self.hyperparameters) != 1:
                    raise ValueError('hyperparameters must be a list containing a single dictionary')
                self.hyperparameter = self.hyperparameters[0]
                self.hyperparameters = None
        return self


@register_action
class TrainAction(Action):
    TRAIN_PROGRESS = {
        'dataset': {
            'proportion': 20,
        },
        'train': {
            'proportion': 75,
        },
        'model_upload': {
            'proportion': 5,
        },
    }

    TUNE_PROGRESS = {
        'dataset': {
            'proportion': 20,
        },
        'trials': {
            'proportion': 75,
        },
        'model_upload': {
            'proportion': 5,
        },
    }

    """
    **Important notes when using train with is_tune=True:**

    1. Path to the model output (which is the return value of your train function)
       should be set to the checkpoint_output attribute of the run object **before**
       starting the training.
    2. Before exiting the training function, report the results to Tune.
    3. When using own tune.py, take note of the difference in the order of parameters.
       tune() function starts with hyperparameter, run, dataset, checkpoint, **kwargs
       whereas the train() function starts with run, dataset, hyperparameter, checkpoint, **kwargs.
    ----
    1)
    Set the output path for the checkpoint to export best model

    output_path = Path('path/to/your/weights')
    run.checkpoint_output = str(output_path)

    2)
    Before exiting the training function, report the results to Tune.
    The results_dict should contain the metrics you want to report.

    Example: (In train function)
    results_dict = {
        "accuracy": accuracy,
        "loss": loss,
        # Add other metrics as needed
    }
    if hasattr(self.dm_run, 'is_tune') and self.dm_run.is_tune:
        tune.report(results_dict, checkpoint=tune.Checkpoint.from_directory(self.dm_run.checkpoint_output))


    3)
    tune() function takes hyperparameter, run, dataset, checkpoint, **kwargs in that order
    whereas train() function takes run, dataset, hyperparameter, checkpoint, **kwargs in that order.

    """

    name = 'train'
    category = PluginCategory.NEURAL_NET
    method = RunMethod.JOB
    run_class = TrainRun
    params_model = TrainParams
    progress_categories = None

    def __init__(self, params, plugin_config, requirements=None, envs=None, job_id=None, direct=False, debug=False):
        selected = self.TUNE_PROGRESS if (params or {}).get('is_tune') else self.TRAIN_PROGRESS
        self.progress_categories = copy.deepcopy(selected)
        super().__init__(
            params, plugin_config, requirements=requirements, envs=envs, job_id=job_id, direct=direct, debug=debug
        )

    def start(self):
        try:
            if self.params.get('is_tune', False):
                return self._start_tune()
            return self._start_train()
        finally:
            # Always emit completion log so backend can record end time even on failures
            self.run.end_log()

    def _start_train(self):
        """Original train logic"""
        hyperparameter = self.params.get('hyperparameter')
        if hyperparameter is None:
            hyperparameters = self.params.get('hyperparameters') or []
            if not hyperparameters:
                raise ValueError('hyperparameter is missing for train mode')
            hyperparameter = hyperparameters[0]
            # Persist the normalized form so later steps (e.g., create_model) find it
            self.params['hyperparameter'] = hyperparameter

        # download dataset
        self.run.log_message('Preparing dataset for training.')
        input_dataset = self.get_dataset()

        # retrieve checkpoint
        checkpoint = None
        if self.params['checkpoint']:
            self.run.log_message('Retrieving checkpoint.')
            checkpoint = self.get_model(self.params['checkpoint'])

        # train dataset
        self.run.log_message('Starting model training.')
        result = self.entrypoint(self.run, input_dataset, hyperparameter, checkpoint=checkpoint)

        # upload model_data
        self.run.log_message('Registering model data.')
        self.run.set_progress(0, 1, category='model_upload')
        model = self.create_model(result)
        self.run.set_progress(1, 1, category='model_upload')

        return {'model_id': model['id'] if model else None}

    def _start_tune(self):
        """Tune logic using Ray Tune for hyperparameter optimization"""
        from ray import tune

        # Ensure Ray is connected to the cluster so GPU resources are visible to trials
        self.ray_init()

        class _TuneTrialsLoggingCallback(tune.Callback):
            """Capture Ray Tune trial table snapshots and forward them to run.log_trials."""

            BASE_COLUMNS = ('trial_id', 'status')
            METRIC_COLUMN_LIMIT = 4
            RESERVED_RESULT_KEYS = {
                'config',
                'date',
                'done',
                'experiment_id',
                'experiment_state',
                'experiment_tag',
                'hostname',
                'iterations_since_restore',
                'logdir',
                'node_ip',
                'pid',
                'restored_from_trial_id',
                'time_since_restore',
                'time_this_iter_s',
                'time_total',
                'time_total_s',
                'timestamp',
                'timesteps_since_restore',
                'timesteps_total',
                'training_iteration',
                'trial_id',
            }

            def __init__(self, run):
                self.run = run
                self.trial_rows: Dict[str, Dict[str, object]] = {}
                self.config_keys: list[str] = []
                self.metric_keys: list[str] = []
                self._last_snapshot = None

            def on_trial_result(self, iteration, trials, trial, result, **info):
                self._record_trial(trial, result, status_override='RUNNING')
                self._emit_snapshot()

            def on_trial_complete(self, iteration, trials, trial, **info):
                self._record_trial(trial, getattr(trial, 'last_result', None), status_override='TERMINATED')
                self._emit_snapshot()

            def on_trial_error(self, iteration, trials, trial, **info):
                self._record_trial(trial, getattr(trial, 'last_result', None), status_override='ERROR')
                self._emit_snapshot()

            def on_step_end(self, iteration, trials, **info):
                updated = False
                for trial in trials or []:
                    status = getattr(trial, 'status', None)
                    existing = self.trial_rows.get(trial.trial_id)
                    existing_status = existing.get('status') if existing else None
                    if existing is None or (status and status != existing_status):
                        self._record_trial(
                            trial,
                            getattr(trial, 'last_result', None),
                            status_override=status,
                        )
                        updated = True
                if updated:
                    self._emit_snapshot()

            def _record_trial(self, trial, result, status_override=None):
                if not self.run or not getattr(self.run, 'log_trials', None):
                    return

                row = self.trial_rows.setdefault(trial.trial_id, {})
                result = result or {}
                if not isinstance(result, dict):
                    result = {}

                row['trial_id'] = trial.trial_id
                row['status'] = status_override or getattr(trial, 'status', 'PENDING')
                config_data = self._extract_config(trial.config or {})
                metric_data = self._extract_metrics(result)

                row.update(config_data)
                row.update(metric_data)

                self._track_columns(config_data.keys(), metric_data.keys())

            def _extract_config(self, config):
                flat = {}
                if not isinstance(config, dict):
                    return flat
                for key, value in self._flatten_items(config):
                    serialized = self._serialize_config_value(value)
                    flat[key] = serialized
                return flat

            def _extract_metrics(self, result):
                metrics = {}
                if not isinstance(result, dict):
                    return metrics

                nested = result.get('metrics')
                if isinstance(nested, dict):
                    for key, value in self._flatten_items(nested, prefix='metrics'):
                        serialized = self._serialize_metric_value(value)
                        if serialized is not None:
                            metrics[key] = serialized

                for key, value in result.items():
                    if key in self.RESERVED_RESULT_KEYS or key == 'metrics':
                        continue
                    if isinstance(value, dict):
                        continue
                    serialized = self._serialize_metric_value(value)
                    if serialized is not None:
                        metrics[key] = serialized

                return metrics

            def _track_columns(self, config_keys, metric_keys):
                for key in config_keys:
                    if key not in self.config_keys:
                        self.config_keys.append(key)
                for key in metric_keys:
                    if key not in self.metric_keys and len(self.metric_keys) < self.METRIC_COLUMN_LIMIT:
                        self.metric_keys.append(key)

            def _emit_snapshot(self):
                if not self.trial_rows:
                    return

                base_keys = list(self.BASE_COLUMNS)
                config_keys = list(self.config_keys)
                metric_keys = list(self.metric_keys)
                columns = base_keys + config_keys + metric_keys

                ordered_trials = {}
                flat_rows = []
                for trial_id in sorted(self.trial_rows.keys()):
                    row = self.trial_rows[trial_id]
                    base_values = [row.get(column) for column in base_keys]
                    hyper_values = [row.get(column) for column in config_keys]
                    metric_values = [row.get(column) for column in metric_keys]
                    flat_values = base_values + hyper_values + metric_values
                    ordered_trials[trial_id] = {
                        'base': base_values,
                        'hyperparameters': hyper_values,
                        'metrics': metric_values,
                    }
                    flat_rows.append((trial_id, tuple(flat_values)))

                snapshot = (
                    tuple(columns),
                    tuple(flat_rows),
                )
                if snapshot == self._last_snapshot:
                    return
                self._last_snapshot = snapshot

                self.run.log_trials(
                    base=base_keys,
                    trials=ordered_trials,
                    hyperparameters=config_keys,
                    metrics=metric_keys,
                    best_trial='',
                )
                self._update_trials_progress()

            def _flatten_items(self, data, prefix=None):
                if not isinstance(data, dict):
                    return
                for key, value in data.items():
                    key_str = str(key)
                    current = f'{prefix}/{key_str}' if prefix else key_str
                    if isinstance(value, dict):
                        yield from self._flatten_items(value, current)
                    else:
                        yield current, value

            def _update_trials_progress(self):
                total = getattr(self.run, 'num_samples', None)
                if not total:
                    return

                completed_statuses = {'TERMINATED', 'ERROR'}
                completed = sum(1 for row in self.trial_rows.values() if row.get('status') in completed_statuses)
                completed = min(completed, total)

                try:
                    self.run.set_progress(completed, total, category='trials')
                except Exception:  # pragma: no cover - safeguard against logging failures
                    self.run.log_message('Failed to update trials progress.')

            def _serialize_config_value(self, value):
                if isinstance(value, (str, bool)) or value is None:
                    return value
                if isinstance(value, Number):
                    return float(value) if not isinstance(value, bool) else value
                return str(value)

            def _serialize_metric_value(self, value):
                if isinstance(value, Number):
                    return float(value)
                return None

        # Mark run as tune
        self.run.is_tune = True

        # download dataset
        self.run.log_message('Preparing dataset for hyperparameter tuning.')
        input_dataset = self.get_dataset()

        # retrieve checkpoint
        checkpoint = None
        if self.params['checkpoint']:
            self.run.log_message('Retrieving checkpoint.')
            checkpoint = self.get_model(self.params['checkpoint'])

        # train dataset
        self.run.log_message('Starting training for hyperparameter tuning.')

        # Save num_samples to TrainRun for logging
        self.run.num_samples = self.params['tune_config']['num_samples']

        tune_config = self.params['tune_config']

        entrypoint = self.entrypoint
        if not self._tune_override_exists():
            # entrypoint must be train entrypoint
            train_entrypoint = entrypoint

            def _tune(param_space, run, dataset, checkpoint=None, **kwargs):
                return train_entrypoint(run, dataset, param_space, checkpoint, **kwargs)

            entrypoint = _tune

        entrypoint = self._wrap_tune_entrypoint(entrypoint, tune_config.get('metric'))

        train_fn = tune.with_parameters(entrypoint, run=self.run, dataset=input_dataset, checkpoint=checkpoint)

        # Extract search_alg and scheduler as separate objects to avoid JSON serialization issues
        search_alg = self.convert_tune_search_alg(tune_config)
        scheduler = self.convert_tune_scheduler(tune_config)

        # Create a copy of tune_config without non-serializable objects
        tune_config_dict = {
            'mode': tune_config.get('mode'),
            'metric': tune_config.get('metric'),
            'num_samples': tune_config.get('num_samples', 1),
            'max_concurrent_trials': tune_config.get('max_concurrent_trials'),
        }

        # Add search_alg and scheduler to tune_config_dict only if they exist
        if search_alg is not None:
            tune_config_dict['search_alg'] = search_alg
        if scheduler is not None:
            tune_config_dict['scheduler'] = scheduler

        hyperparameters = self.params['hyperparameters']
        param_space = self.convert_tune_params(hyperparameters)
        temp_path = tempfile.TemporaryDirectory()
        trials_logger = _TuneTrialsLoggingCallback(self.run)

        trainable = tune.with_resources(train_fn, {'cpu': 1, 'gpu': 0.5})
        print('tune_config :', tune_config)
        print('tune_config_dict :', tune_config_dict)
        #        print('self.tune_resources :', self.tune_resources)
        #        trainable = tune.with_resources(train_fn, self.tune_resources)

        tuner = tune.Tuner(
            trainable,
            tune_config=tune.TuneConfig(**tune_config_dict),
            run_config=tune.RunConfig(
                name=f'synapse_tune_hpo_{self.job_id}',
                log_to_file=('stdout.log', 'stderr.log'),
                storage_path=temp_path.name,
                callbacks=[trials_logger],
            ),
            param_space=param_space,
        )
        result = tuner.fit()

        trial_models_map, trial_models_summary = self._upload_tune_trial_models(result)

        best_result = result.get_best_result()
        artifact_path = self._get_tune_artifact_path(best_result)
        self._override_best_trial(best_result, artifact_path)

        # upload model_data
        self.run.log_message('Registering best model data.')
        self.run.set_progress(0, 1, category='model_upload')
        if artifact_path not in trial_models_map:
            trial_models_map[artifact_path] = self.create_model_from_result(best_result, artifact_path=artifact_path)
        self.run.set_progress(1, 1, category='model_upload')

        return {
            'best_result': best_result.config,
            'trial_models': trial_models_summary,
        }

    def get_dataset(self):
        client = self.run.client
        assert bool(client)

        input_dataset = {}

        ground_truths, count_dataset = client.list_ground_truth_events(
            params={
                'fields': ['category', 'files', 'data'],
                'expand': ['data'],
                'ground_truth_dataset_versions': self.params['dataset'],
            },
            list_all=True,
        )
        self.run.set_progress(0, count_dataset, category='dataset')
        for i, ground_truth in enumerate(ground_truths, start=1):
            self.run.set_progress(i, count_dataset, category='dataset')
            try:
                input_dataset[ground_truth['category']].append(ground_truth)
            except KeyError:
                input_dataset[ground_truth['category']] = [ground_truth]

        return input_dataset

    def get_model(self, model_id):
        model = self.client.get_model(model_id)
        model_file = Path(model['file'])
        output_path = get_temp_path(f'models/{model_file.stem}')
        if not output_path.exists():
            unarchive(model_file, output_path)
        model['path'] = output_path
        return model

    def create_model(self, path):
        params = copy.deepcopy(self.params)
        configuration_fields = ['hyperparameter']
        configuration = {field: params.pop(field) for field in configuration_fields}

        run_name = params.get('name') or f'{self.plugin_release.name}-{self.job_id}'
        unique_name = run_name

        # Derive a stable id from the path for naming
        trial_id = self._resolve_trial_id(type('Result', (), {})(), artifact_path=path)
        if trial_id:
            unique_name = f'{run_name}_{trial_id}'

        params['name'] = unique_name

        temp_dir = tempfile.mkdtemp()
        try:
            input_path = Path(path)
            archive_path = Path(temp_dir, 'archive.zip')
            archive(input_path, archive_path)

            return self.client.create_model({
                'plugin': self.plugin_release.plugin,
                'version': self.plugin_release.version,
                'file': str(archive_path),
                'configuration': configuration,
                **params,
            })
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    @property
    def tune_resources(self):
        resources = {}
        for option in ['num_cpus', 'num_gpus']:
            option_value = self.params.get(option)
            if option_value:
                # Remove the 'num_' prefix and trailing s from the option name
                resources[(lambda s: s[4:-1])(option)] = option_value
        return resources

    def _upload_tune_trial_models(self, result_grid):
        trial_models = {}
        trial_summaries = []

        total_results = len(result_grid)

        for index in range(total_results):
            trial_result = result_grid[index]

            if getattr(trial_result, 'error', None):
                continue

            artifact_path = self._get_tune_artifact_path(trial_result)
            if not artifact_path:
                trial_id = getattr(trial_result, 'trial_id', None)
                self.run.log_message(f'Skipping model registration: no checkpoint path for trial {trial_id}')
                continue

            try:
                model = self.create_model_from_result(trial_result, artifact_path=artifact_path)
            except Exception as exc:  # pragma: no cover - best effort logging
                self.run.log_message(f'Failed to register model for trial at {artifact_path}: {exc}')
                continue

            if model:
                trial_models[artifact_path] = model
                trial_summaries.append({
                    'trial_logdir': artifact_path,
                    'model_id': model.get('id'),
                    'config': getattr(trial_result, 'config', None),
                    'metrics': getattr(trial_result, 'metrics', None),
                })

        return trial_models, trial_summaries

    def _override_best_trial(self, best_result, artifact_path=None):
        if not best_result:
            return

        best_config = getattr(best_result, 'config', None)
        if not isinstance(best_config, dict):
            return

        if artifact_path is None:
            artifact_path = self._get_tune_artifact_path(best_result)

        trial_id = self._resolve_trial_id(best_result, artifact_path)

        if not trial_id:
            self.run.log_message('Skipping override_best_trial request: trial_id missing.')
            return

        payload = {'trial_id': trial_id, **best_config}

        url = f'trains/{self.job_id}/override_best_trial/'
        self.run.log_message(f'Calling override_best_trial: {url} payload={payload}')

        try:
            self.client._put(url, data=payload)
            # Log trials with best_trial after successful PUT request
            last_snapshot = getattr(self.run, '_last_trials_payload', None)
            if isinstance(last_snapshot, dict) and 'trials' in last_snapshot:
                final_snapshot = copy.deepcopy(last_snapshot)
                final_snapshot['best_trial'] = trial_id
                self.run.log_trials(data=final_snapshot)
            else:
                self.run.log_trials(best_trial=trial_id)
        except ClientError as exc:  # pragma: no cover - network failure should not break run
            self.run.log_message(f'Failed to override best trial: {exc}')

    def create_model_from_result(self, result, *, artifact_path=None):
        params = copy.deepcopy(self.params)
        configuration_fields = ['hyperparameters']
        configuration = {field: params.pop(field) for field in configuration_fields}
        configuration['tune_trial'] = {
            'config': getattr(result, 'config', None),
            'metrics': getattr(result, 'metrics', None),
            'logdir': artifact_path or getattr(result, 'path', None),
        }

        if artifact_path is None:
            artifact_path = self._get_tune_artifact_path(result)

        if not artifact_path:
            raise ValueError('No checkpoint path available to create model from result.')

        temp_dir = tempfile.mkdtemp()
        archive_path = Path(temp_dir, 'archive.zip')

        # Archive tune results
        # https://docs.ray.io/en/latest/tune/tutorials/tune_get_data_in_and_out.html#getting-data-out-of-tune-using-checkpoints-other-artifacts
        archive(artifact_path, archive_path)

        unique_name = params.get('name') or f'{self.plugin_release.name}-{self.job_id}'
        trial_id = self._resolve_trial_id(result, artifact_path)
        if trial_id:
            unique_name = f'{unique_name}_{trial_id}'
        params['name'] = unique_name

        try:
            return self.client.create_model({
                'plugin': self.plugin_release.plugin,
                'version': self.plugin_release.version,
                'file': str(archive_path),
                'configuration': configuration,
                **params,
            })
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    def convert_tune_scheduler(tune_config):
        """
        Convert YAML hyperparameter configuration to a Ray Tune scheduler.

        Args:
            tune_config (dict): Hyperparameter configuration.

        Returns:
            object: Ray Tune scheduler instance.

        Supported schedulers:
            - 'fifo': FIFOScheduler (default)
            - 'hyperband': HyperBandScheduler
        """

        from ray.tune.schedulers import (
            ASHAScheduler,
            FIFOScheduler,
            HyperBandScheduler,
            MedianStoppingRule,
            PopulationBasedTraining,
        )

        if tune_config.get('scheduler') is None:
            return None

        scheduler_map = {
            'fifo': FIFOScheduler,
            'asha': ASHAScheduler,
            'hyperband': HyperBandScheduler,
            'pbt': PopulationBasedTraining,
            'median': MedianStoppingRule,
        }

        scheduler_type = tune_config['scheduler'].get('name', 'fifo').lower()
        scheduler_class = scheduler_map.get(scheduler_type, FIFOScheduler)

        # 옵션이 있는 경우 전달하고, 없으면 기본 생성자 호출
        options = tune_config['scheduler'].get('options')

        # options가 None이거나 빈 딕셔너리가 아닌 경우에만 전달
        scheduler = scheduler_class(**options) if options else scheduler_class()

        return scheduler

    @staticmethod
    def convert_tune_search_alg(tune_config):
        """
        Convert YAML hyperparameter configuration to Ray Tune search algorithm.

        Args:
            tune_config (dict): Hyperparameter configuration.

        Returns:
            object: Ray Tune search algorithm instance or None

        Supported search algorithms:
            - 'bayesoptsearch': Bayesian optimization
            - 'hyperoptsearch': Tree-structured Parzen Estimator
            - 'basicvariantgenerator': Random search (default)
        """

        if tune_config.get('search_alg') is None:
            return None

        search_alg_name = tune_config['search_alg']['name'].lower()
        metric = tune_config['metric']
        mode = tune_config['mode']
        points_to_evaluate = tune_config['search_alg'].get('points_to_evaluate', None)

        if search_alg_name == 'axsearch':
            from ray.tune.search.ax import AxSearch

            search_alg = AxSearch(metric=metric, mode=mode)
        elif search_alg_name == 'bayesoptsearch':
            from ray.tune.search.bayesopt import BayesOptSearch

            search_alg = BayesOptSearch(metric=metric, mode=mode)
        elif search_alg_name == 'hyperoptsearch':
            from ray.tune.search.hyperopt import HyperOptSearch

            search_alg = HyperOptSearch(metric=metric, mode=mode)
        elif search_alg_name == 'optunasearch':
            from ray.tune.search.optuna import OptunaSearch

            search_alg = OptunaSearch(metric=metric, mode=mode)
        elif search_alg_name == 'basicvariantgenerator':
            from ray.tune.search.basic_variant import BasicVariantGenerator

            search_alg = BasicVariantGenerator(
                points_to_evaluate=points_to_evaluate, max_concurrent=tune_config['max_concurrent_trials']
            )
        else:
            raise ValueError(
                f'Unsupported search algorithm: {search_alg_name}. '
                f'Supported algorithms are: bayesoptsearch, hyperoptsearch, basicvariantgenerator'
            )

        return search_alg

    @staticmethod
    def convert_tune_params(param_list):
        """
        Convert YAML hyperparameter configuration to Ray Tune parameter dictionary.

        Args:
            param_list (list): List of hyperparameter configurations.

        Returns:
            dict: Ray Tune parameter dictionary
        """
        from ray import tune

        param_handlers = {
            'uniform': lambda p: tune.uniform(p['min'], p['max']),
            'quniform': lambda p: tune.quniform(p['min'], p['max']),
            'loguniform': lambda p: tune.loguniform(p['min'], p['max'], p['base']),
            'qloguniform': lambda p: tune.qloguniform(p['min'], p['max'], p['base']),
            'randn': lambda p: tune.randn(p['mean'], p['sd']),
            'qrandn': lambda p: tune.qrandn(p['mean'], p['sd']),
            'randint': lambda p: tune.randint(p['min'], p['max']),
            'qrandint': lambda p: tune.qrandint(p['min'], p['max']),
            'lograndint': lambda p: tune.lograndint(p['min'], p['max'], p['base']),
            'qlograndint': lambda p: tune.qlograndint(p['min'], p['max'], p['base']),
            'choice': lambda p: tune.choice(p['options']),
            'grid_search': lambda p: tune.grid_search(p['options']),
        }

        param_space = {}

        for param in param_list:
            name = param['name']
            param_type = param['type']

            if param_type in param_handlers:
                param_space[name] = param_handlers[param_type](param)
            else:
                raise ValueError(f'Unknown parameter type: {param_type}')

        return param_space

    @staticmethod
    def _tune_override_exists(module_path='plugin.tune') -> bool:
        try:
            import_string(module_path)
            return True
        except ImportError:
            return False

    @staticmethod
    def _resolve_trial_id(result, artifact_path: Optional[str] = None) -> Optional[str]:
        """
        Return a stable trial_id.

        Priority:
            1. result.trial_id (Ray provided)
            2. metrics['trial_id'] if present
            3. Deterministic hash of artifact_path
        """
        trial_id = getattr(result, 'trial_id', None)
        if trial_id:
            return str(trial_id)

        metrics = getattr(result, 'metrics', None)
        if isinstance(metrics, dict):
            trial_id = metrics.get('trial_id')
            if trial_id:
                return str(trial_id)

        if artifact_path:
            import hashlib

            return hashlib.sha1(str(artifact_path).encode()).hexdigest()[:12]

        return None

    def _get_tune_artifact_path(self, result) -> Optional[str]:
        """
        Determine the artifact/checkpoint path for a Ray Tune result.

        Priority:
            1. checkpoint_output provided via metrics (if present)
            2. Explicit checkpoint path reported by Ray (result.checkpoint.*)
        No fallback to result.path to avoid mixing with trial logdir.
        """
        metrics = getattr(result, 'metrics', None)
        if isinstance(metrics, dict):
            for key in ('checkpoint_output', 'checkpoint', 'result'):
                path = metrics.get(key)
                if path:
                    return str(path)

        checkpoint = getattr(result, 'checkpoint', None)
        if checkpoint:
            for attr in ('path', '_local_path', '_uri'):
                path = getattr(checkpoint, attr, None)
                if path:
                    return str(path)
            try:
                tmp_dir = tempfile.mkdtemp()
                checkpoint.to_directory(tmp_dir)
                return tmp_dir
            except Exception:
                pass

        return None

    def _wrap_tune_entrypoint(self, entrypoint: Callable, metric_key: Optional[str]) -> Callable:
        def _wrapped(*args, **kwargs):
            last_metrics: Optional[Dict[str, float]] = None

            try:
                from ray import tune as ray_tune
            except ImportError:
                ray_tune = None

            if ray_tune and hasattr(ray_tune, 'report'):
                original_report = ray_tune.report

                def caching_report(metrics, *r_args, **r_kwargs):
                    nonlocal last_metrics
                    if isinstance(metrics, dict):
                        last_metrics = metrics.copy()
                    return original_report(metrics, *r_args, **r_kwargs)

                ray_tune.report = caching_report
            else:
                original_report = None

            try:
                result = entrypoint(*args, **kwargs)
            finally:
                if ray_tune and original_report:
                    ray_tune.report = original_report

            payload = self._normalize_tune_result(result, metric_key)
            if last_metrics:
                merged = last_metrics.copy()
                merged.update(payload)
                payload = merged

            if metric_key and metric_key not in payload:
                payload[metric_key] = (last_metrics or {}).get(metric_key, 0.0)

            return payload

        wrapper_name = getattr(entrypoint, '__name__', None)
        if wrapper_name and (wrapper_name.startswith('_') or wrapper_name == '<lambda>'):
            wrapper_name = None
        final_name = wrapper_name or f'trial_{hash(entrypoint) & 0xFFFF:X}'
        _wrapped.__name__ = final_name
        _wrapped.__qualname__ = final_name

        return _wrapped

    @staticmethod
    def _normalize_tune_result(result, metric_key: Optional[str]) -> Dict:
        if isinstance(result, dict):
            return result

        if isinstance(result, Number):
            target_key = metric_key or 'result'
            return {target_key: result}

        return {'result': result}

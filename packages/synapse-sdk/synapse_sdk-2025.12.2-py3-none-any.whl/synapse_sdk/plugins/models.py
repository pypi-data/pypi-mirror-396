import os
from datetime import datetime
from functools import cached_property
from typing import Any, Dict

from pydantic import BaseModel

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.devtools.config import get_backend_config
from synapse_sdk.loggers import BackendLogger, ConsoleLogger
from synapse_sdk.plugins.utils import read_plugin_config
from synapse_sdk.shared import needs_sentry_init
from synapse_sdk.shared.enums import Context
from synapse_sdk.utils.storage import get_storage
from synapse_sdk.utils.string import hash_text


class PluginRelease:
    config: Dict[str, Any]
    envs = None

    def __init__(self, config=None, plugin_path=None, envs=None):
        if config:
            self.config = config
        else:
            self.config = read_plugin_config(plugin_path=plugin_path)
        self.envs = envs

    @cached_property
    def plugin(self):
        return self.config['code']

    @cached_property
    def version(self):
        return self.config['version']

    @cached_property
    def code(self):
        return f'{self.plugin}@{self.version}'

    @cached_property
    def category(self):
        return self.config['category']

    @cached_property
    def name(self):
        return self.config['name']

    @cached_property
    def package_manager(self):
        return self.config.get('package_manager', 'pip')

    @cached_property
    def package_manager_options(self):
        # Get user-defined options from config
        user_options = self.config.get('package_manager_options', [])

        if self.package_manager == 'uv':
            defaults = ['--no-cache']
            # Add defaults if not already present
            options_list = defaults.copy()
            for option in user_options:
                if option not in options_list:
                    options_list.append(option)
            return {'uv_pip_install_options': options_list}
        else:
            # For pip, use pip_install_options with --upgrade flag to ensure
            # packages from requirements.txt (like synapse-sdk) override pre-installed versions
            defaults = ['--upgrade']
            options_list = defaults.copy()
            for option in user_options:
                if option not in options_list:
                    options_list.append(option)
            return {'pip_install_options': options_list}

    @cached_property
    def checksum(self):
        return hash_text(self.code)

    @cached_property
    def actions(self):
        return list(self.config['actions'].keys())

    def setup_runtime_env(self):
        import ray
        from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy
        from ray.util.state import list_nodes

        @ray.remote
        def warm_up():
            pass

        extra_runtime_env = {}

        if needs_sentry_init():
            extra_runtime_env['worker_process_setup_hook'] = 'synapse_sdk.shared.worker_process_setup_hook'

        nodes = list_nodes(address=self.envs['RAY_DASHBOARD_URL'])
        node_ids = [n['node_id'] for n in nodes]
        for node_id in node_ids:
            strategy = NodeAffinitySchedulingStrategy(node_id=node_id, soft=False)

            warm_up.options(
                runtime_env={
                    self.package_manager: {
                        'packages': ['-r ${RAY_RUNTIME_ENV_CREATE_WORKING_DIR}/requirements.txt']
                        ** self.package_manager_options
                    },
                    'working_dir': self.get_url(self.envs['SYNAPSE_PLUGIN_STORAGE']),
                    **extra_runtime_env,
                },
                scheduling_strategy=strategy,
            ).remote()

    def get_action_config(self, action):
        return self.config['actions'][action]

    def get_url(self, storage_url):
        storage = get_storage(storage_url)
        return storage.get_url(f'{self.checksum}.zip')

    def get_serve_url(self, serve_address, path):
        return os.path.join(serve_address, self.checksum, path)


class Run:
    """Run class for manage plugin run istance.

    Attrs:
        job_id: plugin run job id
        context: plugin run context
        client: backend client for communicate with backend
        logger: logger for log plugin run events
    """

    logger = None
    job_id = None
    context = None
    client = None

    class DevLog(BaseModel):
        """Model for developer log entries.

        Records custom events and information that plugin developers want to track
        during plugin execution for debugging and monitoring purposes.

        Attributes:
            event_type (str): Type/category of the development event
            message (str): Descriptive message about the event
            data (dict | None): Optional additional data/context
            level (Context): Event status/severity level
            created (str): Timestamp when event occurred
        """

        event_type: str
        message: str
        data: dict | None = None
        level: Context
        created: str

    def __init__(self, job_id, context=None):
        self.job_id = job_id
        self.context = context or {}
        config = get_backend_config()
        if config:
            self.client = BackendClient(
                config['host'],
                access_token=config['token'],
            )
        else:
            # Handle missing environment variables for test environments
            envs = self.context.get('envs', {})
            host = envs.get('SYNAPSE_PLUGIN_RUN_HOST', os.getenv('SYNAPSE_PLUGIN_RUN_HOST', 'http://localhost:8000'))
            token = envs.get('SYNAPSE_PLUGIN_RUN_USER_TOKEN', os.getenv('SYNAPSE_PLUGIN_RUN_USER_TOKEN'))
            tenant = envs.get('SYNAPSE_PLUGIN_RUN_TENANT', os.getenv('SYNAPSE_PLUGIN_RUN_TENANT'))

            self.client = BackendClient(
                host,
                token=token,
                tenant=tenant,
            )
        self.set_logger()

    def set_logger(self):
        kwargs = {
            'progress_categories': self.context.get('progress_categories'),
            'metrics_categories': self.context.get('metrics_categories'),
        }

        if self.job_id:
            self.logger = BackendLogger(self.client, self.job_id, **kwargs)
        else:
            self.logger = ConsoleLogger(**kwargs)

    def set_progress(self, current, total, category=''):
        self.logger.set_progress(current, total, category)

    def set_progress_failed(self, category: str | None = None):
        """Mark progress as failed with elapsed time but no completion.

        This method should be called when an operation fails to indicate that
        no progress was made, but still track how long the operation ran before failing.

        Args:
            category (str | None): progress category
        """
        self.logger.set_progress_failed(category)

    def set_metrics(self, value: Dict[Any, Any], category: str):
        self.logger.set_metrics(value, category)

    def log(self, event, data, file=None):
        self.logger.log(event, data, file=file)

    def log_message(self, message, context=Context.INFO.value):
        self.logger.log('message', {'context': context, 'content': message})

    def log_dev_event(self, message: str, data: dict | None = None, level: Context = Context.INFO):
        """Log development event for plugin developers.

        This function allows plugin developers to log custom events and information
        during plugin execution for debugging, monitoring, and development purposes.
        The event_type is automatically constructed as '{action_name}_dev_log' and cannot
        be modified by plugin developers.

        Args:
            message (str): Descriptive message about the event
            data (dict | None): Optional additional data or context to include
            level (Context): Event severity level (INFO, WARNING, DANGER, SUCCESS)

        Example:
            >>> run = Run(job_id, context)
            >>> run.log_dev_event('Data validation completed', {'records_count': 100})
            >>> run.log_dev_event('Processing time recorded', {'duration_ms': 1500})
            >>> run.log_dev_event('Variable state at checkpoint', {'variable_x': 42}, level=Context.WARNING)
        """
        # Construct event_type from action name - this cannot be modified by developers
        action_name = self.context.get('action_name', 'unknown')
        event_type = f'{action_name}_dev_log'

        # Log the structured event for development tracking only
        # Do NOT use log_message to avoid showing debug logs to end users
        now = datetime.now().isoformat()
        self.log(
            'dev_event',
            self.DevLog(
                event_type=event_type,
                message=message,
                data=data,
                level=level,
                created=now,
            ).model_dump(),
        )

    def end_log(self):
        self.log_message('Plugin run is complete.')

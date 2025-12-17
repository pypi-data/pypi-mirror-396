from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from synapse_sdk.plugins.categories.neural_net.actions.train import TrainParams


@pytest.fixture
def base_params():
    action_mock = Mock()
    action_mock.client.exists.return_value = False
    return {
        'name': 'test',
        'description': 'test description',
        'dataset': 1,
        'is_tune': False,
        'action': action_mock,
        'checkpoint': None,
    }


def test_validate_tune_params_normal_train_with_hyperparameter(base_params):
    params = base_params.copy()
    params['hyperparameter'] = {'lr': 0.01}
    tp = TrainParams.model_validate(params, context={'action': base_params['action']})
    assert tp.hyperparameter == {'lr': 0.01}


def test_validate_tune_params_normal_train_with_hyperparameters(base_params):
    params = base_params.copy()
    params['hyperparameters'] = [{'lr': 0.01}]
    tp = TrainParams.model_validate(params, context={'action': base_params['action']})
    assert tp.hyperparameter == {'lr': 0.01}
    assert tp.hyperparameters is None


def test_validate_tune_params_normal_train_with_both_error(base_params):
    params = base_params.copy()
    params['hyperparameter'] = {'lr': 0.01}
    params['hyperparameters'] = [{'lr': 0.01}]
    with pytest.raises(ValidationError):
        TrainParams.model_validate(params, context={'action': base_params['action']})


def test_validate_tune_params_normal_train_with_neither_error(base_params):
    params = base_params.copy()
    with pytest.raises(ValidationError):
        TrainParams.model_validate(params, context={'action': base_params['action']})


def test_validate_tune_params_tune_mode_with_hyperparameters(base_params):
    params = base_params.copy()
    params['is_tune'] = True
    params['hyperparameters'] = [{'name': 'lr', 'type': 'uniform', 'min': 0.01, 'max': 0.1}]
    params['tune_config'] = {'mode': 'max', 'metric': 'acc'}
    tp = TrainParams.model_validate(params, context={'action': base_params['action']})
    assert tp.hyperparameters == [{'name': 'lr', 'type': 'uniform', 'min': 0.01, 'max': 0.1}]


def test_validate_tune_params_tune_mode_with_hyperparameter_error(base_params):
    params = base_params.copy()
    params['is_tune'] = True
    params['hyperparameter'] = {'lr': 0.01}
    params['hyperparameters'] = [{'name': 'lr', 'type': 'uniform', 'min': 0.01, 'max': 0.1}]
    params['tune_config'] = {'mode': 'max', 'metric': 'acc'}
    with pytest.raises(ValidationError):
        TrainParams.model_validate(params, context={'action': base_params['action']})


def test_validate_tune_params_tune_mode_without_hyperparameters_error(base_params):
    params = base_params.copy()
    params['is_tune'] = True
    params['tune_config'] = {'mode': 'max', 'metric': 'acc'}
    with pytest.raises(ValidationError):
        TrainParams.model_validate(params, context={'action': base_params['action']})

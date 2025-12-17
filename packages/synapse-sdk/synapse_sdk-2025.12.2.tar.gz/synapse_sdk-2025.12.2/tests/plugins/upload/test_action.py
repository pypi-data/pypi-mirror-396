from unittest.mock import Mock, patch

from synapse_sdk.plugins.categories.upload.actions.upload import UploadAction, UploadParams, UploadRun
from synapse_sdk.plugins.categories.upload.actions.upload.context import UploadContext
from synapse_sdk.plugins.enums import PluginCategory, RunMethod


class TestUploadAction:
    """Test UploadAction class."""

    def test_action_class_attributes(self):
        """Test UploadAction class attributes."""
        assert UploadAction.name == 'upload'
        assert UploadAction.category == PluginCategory.UPLOAD
        assert UploadAction.method == RunMethod.JOB
        assert UploadAction.run_class == UploadRun
        assert UploadAction.params_model == UploadParams

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_action_initialization(self, mock_config):
        """Test UploadAction initialization."""
        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config, job_id='test-job-123')

        assert action.params == params
        assert action.plugin_config == plugin_config
        assert action.job_id == 'test-job-123'
        assert action.direct is False
        assert action.debug is False

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_action_initialization_with_optional_params(self, mock_config):
        """Test UploadAction initialization with optional parameters."""
        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        requirements = ['pandas>=1.0.0', 'openpyxl>=3.0.0']
        envs = {'CUSTOM_ENV': 'test_value'}

        action = UploadAction(
            params=params,
            plugin_config=plugin_config,
            requirements=requirements,
            envs=envs,
            job_id='test-job-456',
            direct=True,
            debug=True,
        )

        assert action.requirements == requirements
        assert 'CUSTOM_ENV' in action.envs
        assert action.envs['CUSTOM_ENV'] == 'test_value'
        assert action.direct is True
        assert action.debug is True

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_action_run_instance_creation(self, mock_config):
        """Test that UploadAction creates correct run instance."""
        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config, job_id='test-job-789')

        # Verify run instance is created and is the correct type
        assert action.run is not None
        assert isinstance(action.run, UploadRun)
        assert action.run.job_id == 'test-job-789'

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_action_inheritance(self, mock_config):
        """Test UploadAction inherits from base Action class."""
        from synapse_sdk.plugins.categories.base import Action

        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config)

        assert isinstance(action, Action)
        assert hasattr(action, 'validate_params')
        assert hasattr(action, 'run_action')
        assert hasattr(action, 'start')

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_action_required_envs(self, mock_config):
        """Test UploadAction has required environment variables."""
        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config)

        # Verify required environment variables are defined
        required_envs = action.REQUIRED_ENVS
        assert 'RAY_ADDRESS' in required_envs
        assert 'RAY_DASHBOARD_URL' in required_envs
        assert 'RAY_SERVE_ADDRESS' in required_envs
        assert 'SYNAPSE_PLUGIN_STORAGE' in required_envs

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_workflow_configuration(self, mock_config):
        """Test that workflow steps are properly configured."""
        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config)

        # Verify steps are registered
        assert len(action.step_registry) == 8
        step_names = action.step_registry.get_step_names()

        expected_steps = [
            'initialize',
            'process_metadata',
            'analyze_collection',
            'organize_files',
            'validate_files',
            'upload_files',
            'generate_data_units',
            'cleanup',
        ]

        assert step_names == expected_steps

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_strategy_configuration(self, mock_config):
        """Test strategy configuration."""
        params = {
            'name': 'Test Upload',
            'path': '/test/path',
            'storage': 1,
            'data_collection': 1,
            'is_recursive': True,
            'creating_data_unit_batch_size': 5,
        }

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config)

        # Create a mock context for strategy configuration
        mock_context = Mock(spec=UploadContext)

        strategies = action._configure_strategies(mock_context)

        assert 'validation' in strategies
        assert 'file_discovery' in strategies
        assert 'metadata' in strategies
        assert 'upload' in strategies
        assert 'data_unit' in strategies

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_get_workflow_summary(self, mock_config):
        """Test getting workflow summary."""
        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config)

        summary = action.get_workflow_summary()

        assert 'steps' in summary
        assert 'step_count' in summary
        assert 'total_progress_weight' in summary
        assert 'available_strategies' in summary

        assert summary['step_count'] == 8
        assert len(summary['steps']) == 8
        assert summary['total_progress_weight'] == 1.0  # Sum of all step weights

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_progress_categories(self, mock_config):
        """Test progress categories are properly configured."""
        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config)

        assert hasattr(action, 'progress_categories')
        assert 'analyze_collection' in action.progress_categories
        assert 'upload_data_files' in action.progress_categories
        assert 'generate_data_units' in action.progress_categories

    @patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
    def test_metrics_categories(self, mock_config):
        """Test metrics categories are properly configured."""
        params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}

        plugin_config = {
            'name': 'upload-plugin',
            'version': '1.0.0',
            'actions': {'upload': {'entrypoint': 'test.entrypoint'}},
        }

        action = UploadAction(params=params, plugin_config=plugin_config)

        assert hasattr(action, 'metrics_categories')
        assert 'data_files' in action.metrics_categories
        assert 'data_units' in action.metrics_categories

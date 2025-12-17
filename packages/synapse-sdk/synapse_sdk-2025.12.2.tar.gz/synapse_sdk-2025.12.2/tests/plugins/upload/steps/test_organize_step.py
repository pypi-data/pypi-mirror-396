"""Tests for OrganizeFilesStep."""

from pathlib import Path
from unittest.mock import Mock, patch

from synapse_sdk.plugins.categories.upload.actions.upload.context import UploadContext
from synapse_sdk.plugins.categories.upload.actions.upload.enums import LogCode
from synapse_sdk.plugins.categories.upload.actions.upload.steps.organize import OrganizeFilesStep


class TestOrganizeFilesStepMultiPath:
    """Test OrganizeFilesStep with multi-path mode."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_run = Mock()
        self.mock_client = Mock()
        self.step = OrganizeFilesStep()

    @patch('synapse_sdk.utils.storage.get_pathlib')
    def test_execute_multi_path_mode_with_dict_asset_config(self, mock_get_pathlib):
        """Test multi-path mode handles dictionary asset_config correctly.

        This test verifies the fix for the AttributeError bug where asset_config.path
        was incorrectly accessed. The asset_config is a dictionary, not an object,
        so it should use asset_config.get('path', '') instead.

        Regression test for: SYN-5798 - 'dict' object has no attribute 'path'
        """
        # Create mock path
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_get_pathlib.return_value = mock_path

        # Mock file discovery strategy
        mock_strategy = Mock()
        discovered_files = [{'file_path': '/test/images/img1.jpg', 'spec_name': 'images'}]
        mock_strategy.discover.return_value = discovered_files
        mock_strategy.organize.return_value = [
            {
                'dataset_key': 'test_dataset',
                'files': {'images': ['/test/images/img1.jpg']},
                'specs': [{'name': 'images', 'is_required': True, 'extensions': ['.jpg', '.png']}],
            }
        ]

        # Create context with multi-path mode using dictionary-based asset config
        params = {
            'name': 'Test Upload',
            'storage': 1,
            'data_collection': 1,
            'use_single_path': False,  # Multi-path mode
            'assets': {
                'images': {'path': 'test/images', 'is_recursive': True}  # Dictionary, not object
            },
        }
        context = UploadContext(params, self.mock_run, self.mock_client)

        # Set up required context attributes
        context.storage = Mock()
        context.file_specifications = [{'name': 'images', 'is_required': True, 'extensions': ['.jpg', '.png']}]
        context.strategies = {'file_discovery': mock_strategy}
        context.metadata = {}

        # Execute the step
        result = self.step.execute(context)

        # Verify no AttributeError was raised and step succeeded
        assert result.success is True
        assert 'organized_files' in result.data

        # Verify asset_config.get('path', '') was used correctly
        # by checking get_pathlib was called with the correct path
        mock_get_pathlib.assert_called_with(context.storage, 'test/images')

    @patch('synapse_sdk.utils.storage.get_pathlib')
    def test_execute_multi_path_mode_path_not_found_uses_enum_logging(self, mock_get_pathlib):
        """Test that non-existent paths use enum-based logging.

        Verifies that LogCode.ASSET_PATH_NOT_FOUND is used instead of plain string logging.
        """
        # Create mock path that doesn't exist
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = False
        mock_get_pathlib.return_value = mock_path

        # Create context with multi-path mode
        params = {
            'name': 'Test Upload',
            'storage': 1,
            'data_collection': 1,
            'use_single_path': False,
            'assets': {'images': {'path': 'test/nonexistent', 'is_recursive': True}},
        }
        context = UploadContext(params, self.mock_run, self.mock_client)
        context.storage = Mock()
        context.file_specifications = [{'name': 'images', 'is_required': True, 'extensions': ['.jpg']}]
        context.strategies = {'file_discovery': Mock()}
        context.metadata = {}

        # Execute the step
        result = self.step.execute(context)

        # Verify enum-based logging was used
        self.mock_run.log_message_with_code.assert_called()
        calls = self.mock_run.log_message_with_code.call_args_list

        # Check that ASSET_PATH_NOT_FOUND was used
        assert any(call[0][0] == LogCode.ASSET_PATH_NOT_FOUND for call in calls)

    @patch('synapse_sdk.utils.storage.get_pathlib')
    def test_execute_multi_path_mode_path_access_error_uses_enum_logging(self, mock_get_pathlib):
        """Test that path access errors use enum-based logging.

        Verifies that LogCode.ASSET_PATH_ACCESS_ERROR is used instead of plain string logging.
        """
        # Make get_pathlib raise an exception
        mock_get_pathlib.side_effect = Exception('Permission denied')

        # Create context with multi-path mode
        params = {
            'name': 'Test Upload',
            'storage': 1,
            'data_collection': 1,
            'use_single_path': False,
            'assets': {'images': {'path': 'test/restricted', 'is_recursive': True}},
        }
        context = UploadContext(params, self.mock_run, self.mock_client)
        context.storage = Mock()
        context.file_specifications = [{'name': 'images', 'is_required': True, 'extensions': ['.jpg']}]
        context.strategies = {'file_discovery': Mock()}
        context.metadata = {}

        # Execute the step
        result = self.step.execute(context)

        # Verify enum-based logging was used
        self.mock_run.log_message_with_code.assert_called()
        calls = self.mock_run.log_message_with_code.call_args_list

        # Check that ASSET_PATH_ACCESS_ERROR was used
        assert any(call[0][0] == LogCode.ASSET_PATH_ACCESS_ERROR for call in calls)

    @patch('synapse_sdk.utils.storage.get_pathlib')
    def test_execute_multi_path_mode_with_multiple_assets(self, mock_get_pathlib):
        """Test multi-path mode with multiple asset types.

        Ensures that each asset type's path is correctly accessed from the dictionary.
        """
        # Create mock paths
        mock_images_path = Mock(spec=Path)
        mock_images_path.exists.return_value = True

        mock_labels_path = Mock(spec=Path)
        mock_labels_path.exists.return_value = True

        # Mock get_pathlib to return different paths based on input
        def get_pathlib_side_effect(storage, path):
            if 'images' in path:
                return mock_images_path
            elif 'labels' in path:
                return mock_labels_path
            return Mock()

        mock_get_pathlib.side_effect = get_pathlib_side_effect

        # Mock file discovery strategy
        mock_strategy = Mock()
        mock_strategy.discover.side_effect = [
            [{'file_path': '/test/images/img1.jpg', 'spec_name': 'images'}],
            [{'file_path': '/test/labels/label1.json', 'spec_name': 'labels'}],
        ]
        mock_strategy.organize.return_value = [
            {
                'dataset_key': 'test_dataset',
                'files': {
                    'images': ['/test/images/img1.jpg'],
                    'labels': ['/test/labels/label1.json'],
                },
                'specs': [
                    {'name': 'images', 'is_required': True, 'extensions': ['.jpg']},
                    {'name': 'labels', 'is_required': True, 'extensions': ['.json']},
                ],
            }
        ]

        # Create context with multiple assets
        params = {
            'name': 'Test Upload',
            'storage': 1,
            'data_collection': 1,
            'use_single_path': False,
            'assets': {
                'images': {'path': 'test/images', 'is_recursive': True},
                'labels': {'path': 'test/labels', 'is_recursive': False},
            },
        }
        context = UploadContext(params, self.mock_run, self.mock_client)
        context.storage = Mock()
        context.file_specifications = [
            {'name': 'images', 'is_required': True, 'extensions': ['.jpg']},
            {'name': 'labels', 'is_required': True, 'extensions': ['.json']},
        ]
        context.strategies = {'file_discovery': mock_strategy}
        context.metadata = {}

        # Execute the step
        result = self.step.execute(context)

        # Verify both paths were accessed correctly
        assert result.success is True
        assert mock_get_pathlib.call_count >= 2

        # Verify both asset paths were used
        call_args = [call[0][1] for call in mock_get_pathlib.call_args_list]
        assert 'test/images' in call_args
        assert 'test/labels' in call_args

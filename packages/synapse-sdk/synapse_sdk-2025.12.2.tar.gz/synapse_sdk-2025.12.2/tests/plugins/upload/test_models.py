from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.plugins.categories.upload.actions.upload import UploadParams


class TestUploadParams:
    """Test UploadParams pydantic model."""

    def test_upload_params_creation_valid(self):
        """Test creating UploadParams with valid data."""

        # Mock action with client for validators
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_client.get_project.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {
                'name': 'Test Upload',
                'description': 'Test description',
                'path': '/test/path',
                'storage': 1,
                'data_collection': 1,
                'project': 1,
                'excel_metadata_path': 'tests/test_data/metadata.xlsx',
                'is_recursive': True,
                'max_file_size_mb': 100,
                'creating_data_unit_batch_size': 200,
            },
            context=context,
        )

        assert params.name == 'Test Upload'
        assert params.description == 'Test description'
        assert params.path == '/test/path'
        assert params.storage == 1
        assert params.data_collection == 1
        assert params.project == 1
        assert params.excel_metadata_path == 'tests/test_data/metadata.xlsx'
        assert params.is_recursive is True
        assert params.max_file_size_mb == 100
        assert params.creating_data_unit_batch_size == 200

    def test_upload_params_creation_minimal(self):
        """Test creating UploadParams with minimal required fields."""

        # Mock action with client for validators
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}, context=context
        )

        assert params.name == 'Test Upload'
        assert params.description is None
        assert params.path == '/test/path'
        assert params.storage == 1
        assert params.data_collection == 1
        assert params.project is None
        assert params.excel_metadata_path is None
        assert params.is_recursive is True
        assert params.max_file_size_mb == 50
        assert params.creating_data_unit_batch_size == 1

    def test_upload_params_blank_name_validation(self):
        """Test UploadParams validation fails with blank name."""

        # Mock action with client
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        with pytest.raises(ValidationError) as exc_info:
            UploadParams.model_validate(
                {
                    'name': '',  # Blank name should fail
                    'path': '/test/path',
                    'storage': 1,
                    'data_collection': 1,
                },
                context=context,
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['loc'] == ('name',) for error in errors)

    def test_upload_params_storage_validation_success(self):
        """Test storage validation passes when storage exists."""

        # Mock action with client that returns storage
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}, context=context
        )

        assert params.storage == 1
        mock_client.get_storage.assert_called_once_with(1)

    def test_upload_params_storage_validation_failure(self):
        """Test storage validation fails when storage doesn't exist."""

        # Mock action with client that raises ClientError
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.side_effect = ClientError(status=404, reason='Storage not found')
        mock_action.client = mock_client

        context = {'action': mock_action}

        with pytest.raises(ValidationError) as exc_info:
            UploadParams.model_validate(
                {
                    'name': 'Test Upload',
                    'path': '/test/path',
                    'storage': 999,  # Non-existent storage
                    'data_collection': 1,
                },
                context=context,
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['loc'] == ('storage',) for error in errors)

    def test_upload_params_collection_validation_success(self):
        """Test collection validation passes when collection exists."""

        # Mock action with client that returns collection
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}, context=context
        )

        assert params.data_collection == 1
        mock_client.get_data_collection.assert_called_once_with(1)

    def test_upload_params_collection_validation_failure(self):
        """Test collection validation fails when collection doesn't exist."""

        # Mock action with client that raises ClientError for collection
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.side_effect = ClientError(status=404, reason='Collection not found')
        mock_action.client = mock_client

        context = {'action': mock_action}

        with pytest.raises(ValidationError) as exc_info:
            UploadParams.model_validate(
                {
                    'name': 'Test Upload',
                    'path': '/test/path',
                    'storage': 1,
                    'data_collection': 999,  # Non-existent collection
                },
                context=context,
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['loc'] == ('data_collection',) for error in errors)

    def test_upload_params_project_validation_success(self):
        """Test project validation passes when project exists."""

        # Mock action with client that returns project
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_client.get_project.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1, 'project': 1},
            context=context,
        )

        assert params.project == 1
        mock_client.get_project.assert_called_once_with(1)

    def test_upload_params_project_validation_none(self):
        """Test project validation when project is None."""

        # Mock action with client
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1, 'project': None},
            context=context,
        )

        assert params.project is None
        # get_project should not be called when project is None
        mock_client.get_project.assert_not_called()

    def test_excel_metadata_path_with_string(self):
        """Test excel_metadata_path accepts string path."""
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {
                'name': 'Test Upload',
                'path': '/test/path',
                'storage': 1,
                'data_collection': 1,
                'excel_metadata_path': '/path/to/metadata.xlsx',
            },
            context=context,
        )

        assert params.excel_metadata_path == '/path/to/metadata.xlsx'
        assert isinstance(params.excel_metadata_path, str)

    def test_excel_metadata_path_none(self):
        """Test excel_metadata_path can be None (optional field)."""
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {
                'name': 'Test Upload',
                'path': '/test/path',
                'storage': 1,
                'data_collection': 1,
            },
            context=context,
        )

        assert params.excel_metadata_path is None


class TestExcelMetadataPathResolution:
    """Test Excel metadata path resolution strategies."""

    def test_absolute_path_resolution(self, tmp_path):
        """Test resolving absolute path to Excel metadata file."""
        from synapse_sdk.plugins.categories.upload.actions.upload.context import UploadContext
        from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep

        # Create a temporary Excel file
        excel_file = tmp_path / 'metadata.xlsx'
        excel_file.write_text('dummy excel content')

        # Create mock context
        mock_run = Mock()
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.id = 1

        params = {'excel_metadata_path': str(excel_file)}
        context = UploadContext(params, mock_run, mock_client)
        context.storage = mock_storage

        # Test absolute path resolution
        step = ProcessMetadataStep()
        resolved_path = step._resolve_excel_path_from_string(str(excel_file), context)

        assert resolved_path is not None
        assert resolved_path.exists()
        assert resolved_path == excel_file

    def test_storage_relative_path_resolution(self, tmp_path, monkeypatch):
        """Test resolving storage-relative path to Excel metadata file."""
        from synapse_sdk.plugins.categories.upload.actions.upload.context import UploadContext
        from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep

        # Create a temporary Excel file
        storage_base = tmp_path / 'storage'
        storage_base.mkdir()
        excel_file = storage_base / 'metadata.xlsx'
        excel_file.write_text('dummy excel content')

        # Mock get_pathlib to return storage-relative path
        def mock_get_pathlib(storage, relative_path):
            return storage_base / relative_path

        monkeypatch.setattr(
            'synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata.get_pathlib', mock_get_pathlib
        )

        # Create mock context
        mock_run = Mock()
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.id = 1

        params = {'excel_metadata_path': 'metadata.xlsx'}
        context = UploadContext(params, mock_run, mock_client)
        context.storage = mock_storage

        # Test storage-relative path resolution
        step = ProcessMetadataStep()
        resolved_path = step._resolve_excel_path_from_string('metadata.xlsx', context)

        assert resolved_path is not None
        assert resolved_path.exists()
        assert resolved_path.name == 'metadata.xlsx'

    def test_working_directory_relative_path_resolution(self, tmp_path):
        """Test resolving working directory-relative path to Excel metadata file."""
        from synapse_sdk.plugins.categories.upload.actions.upload.context import UploadContext
        from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep

        # Create a temporary Excel file in working directory
        working_dir = tmp_path / 'workdir'
        working_dir.mkdir()
        excel_file = working_dir / 'metadata.xlsx'
        excel_file.write_text('dummy excel content')

        # Create mock context with pathlib_cwd
        mock_run = Mock()
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.id = 1

        params = {'excel_metadata_path': 'metadata.xlsx'}
        context = UploadContext(params, mock_run, mock_client)
        context.storage = mock_storage
        context.pathlib_cwd = working_dir

        # Test working directory-relative path resolution
        step = ProcessMetadataStep()
        resolved_path = step._resolve_excel_path_from_string('metadata.xlsx', context)

        assert resolved_path is not None
        assert resolved_path.exists()
        assert resolved_path == excel_file

    def test_path_resolution_returns_none_when_file_not_found(self):
        """Test that path resolution returns None when file doesn't exist."""
        from synapse_sdk.plugins.categories.upload.actions.upload.context import UploadContext
        from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep

        # Create mock context
        mock_run = Mock()
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.id = 1

        params = {'excel_metadata_path': '/nonexistent/metadata.xlsx'}
        context = UploadContext(params, mock_run, mock_client)
        context.storage = mock_storage

        # Test that non-existent path returns None
        step = ProcessMetadataStep()
        resolved_path = step._resolve_excel_path_from_string('/nonexistent/metadata.xlsx', context)

        assert resolved_path is None

    def test_default_metadata_file_discovery_xlsx(self, tmp_path):
        """Test default metadata file discovery finds meta.xlsx."""
        from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep

        # Create meta.xlsx in working directory
        working_dir = tmp_path / 'workdir'
        working_dir.mkdir()
        meta_file = working_dir / 'meta.xlsx'
        meta_file.write_text('dummy excel content')

        # Test discovery
        step = ProcessMetadataStep()
        discovered_path = step._find_excel_metadata_file(working_dir)

        assert discovered_path is not None
        assert discovered_path.exists()
        assert discovered_path.name == 'meta.xlsx'

    def test_default_metadata_file_discovery_xls_fallback(self, tmp_path):
        """Test default metadata file discovery falls back to meta.xls."""
        from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep

        # Create meta.xls in working directory (no .xlsx)
        working_dir = tmp_path / 'workdir'
        working_dir.mkdir()
        meta_file = working_dir / 'meta.xls'
        meta_file.write_text('dummy excel content')

        # Test discovery
        step = ProcessMetadataStep()
        discovered_path = step._find_excel_metadata_file(working_dir)

        assert discovered_path is not None
        assert discovered_path.exists()
        assert discovered_path.name == 'meta.xls'

    def test_default_metadata_file_discovery_xlsx_priority(self, tmp_path):
        """Test that meta.xlsx takes priority over meta.xls."""
        from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep

        # Create both meta.xlsx and meta.xls
        working_dir = tmp_path / 'workdir'
        working_dir.mkdir()
        xlsx_file = working_dir / 'meta.xlsx'
        xlsx_file.write_text('xlsx content')
        xls_file = working_dir / 'meta.xls'
        xls_file.write_text('xls content')

        # Test that .xlsx is prioritized
        step = ProcessMetadataStep()
        discovered_path = step._find_excel_metadata_file(working_dir)

        assert discovered_path is not None
        assert discovered_path.name == 'meta.xlsx'  # Should prefer .xlsx

    def test_default_metadata_file_discovery_returns_none(self, tmp_path):
        """Test that discovery returns None when no default files exist."""
        from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep

        # Create empty working directory
        working_dir = tmp_path / 'workdir'
        working_dir.mkdir()

        # Test discovery with no files
        step = ProcessMetadataStep()
        discovered_path = step._find_excel_metadata_file(working_dir)

        assert discovered_path is None

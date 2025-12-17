"""Tests for HTTP → Ray GCS conversion utilities."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_ray_module():
    """Mock the ray module and its submodules."""
    # Create mock modules
    mock_ray = MagicMock()
    mock_ray_private = MagicMock()
    mock_runtime_env = MagicMock()
    mock_packaging = MagicMock()

    # Set up the module hierarchy
    mock_ray._private = mock_ray_private
    mock_ray_private.runtime_env = mock_runtime_env
    mock_runtime_env.packaging = mock_packaging

    # Store original modules if they exist
    original_modules = {}
    modules_to_mock = ['ray', 'ray._private', 'ray._private.runtime_env', 'ray._private.runtime_env.packaging']

    for module_name in modules_to_mock:
        if module_name in sys.modules:
            original_modules[module_name] = sys.modules[module_name]

    # Install mocks
    sys.modules['ray'] = mock_ray
    sys.modules['ray._private'] = mock_ray_private
    sys.modules['ray._private.runtime_env'] = mock_runtime_env
    sys.modules['ray._private.runtime_env.packaging'] = mock_packaging

    yield {
        'ray': mock_ray,
        'packaging': mock_packaging,
    }

    # Restore original modules
    for module_name in modules_to_mock:
        if module_name in original_modules:
            sys.modules[module_name] = original_modules[module_name]
        elif module_name in sys.modules:
            del sys.modules[module_name]


class TestConvertHttpToRayGcs:
    """Test suite for convert_http_to_ray_gcs() function."""

    @patch('synapse_sdk.plugins.upload.download_file')
    def test_convert_http_to_ray_gcs_success(self, mock_download, mock_ray_module, mock_http_url, mock_gcs_uri):
        """Test successful HTTP → Ray GCS conversion."""
        # Arrange
        mock_ray_module['ray'].is_initialized.return_value = True
        mock_ray_module['packaging'].get_uri_for_package.return_value = mock_gcs_uri
        mock_ray_module['packaging'].package_exists.return_value = False

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(b'test zip content')
            tmp.flush()
            mock_download.return_value = tmp.name

            try:
                # Act
                from synapse_sdk.plugins.utils import convert_http_to_ray_gcs

                result = convert_http_to_ray_gcs(mock_http_url)

                # Assert
                assert result == mock_gcs_uri
                mock_ray_module['ray'].is_initialized.assert_called_once()
                mock_download.assert_called_once()
                mock_ray_module['packaging'].get_uri_for_package.assert_called_once()
                mock_ray_module['packaging'].package_exists.assert_called_once_with(mock_gcs_uri)
                mock_ray_module['packaging'].upload_package_to_gcs.assert_called_once_with(
                    mock_gcs_uri, b'test zip content'
                )
            finally:
                Path(tmp.name).unlink(missing_ok=True)

    @patch('synapse_sdk.plugins.upload.download_file')
    def test_convert_http_to_ray_gcs_already_exists(self, mock_download, mock_ray_module, mock_http_url, mock_gcs_uri):
        """Test that existing packages in Ray GCS are not re-uploaded (deduplication)."""
        # Arrange
        mock_ray_module['ray'].is_initialized.return_value = True
        mock_ray_module['packaging'].get_uri_for_package.return_value = mock_gcs_uri
        mock_ray_module['packaging'].package_exists.return_value = True  # Already exists

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(b'test zip content')
            tmp.flush()
            mock_download.return_value = tmp.name

            try:
                # Act
                from synapse_sdk.plugins.utils import convert_http_to_ray_gcs

                result = convert_http_to_ray_gcs(mock_http_url)

                # Assert
                assert result == mock_gcs_uri
                mock_ray_module['packaging'].package_exists.assert_called_once_with(mock_gcs_uri)
                # upload_package_to_gcs should NOT be called due to deduplication
                mock_ray_module['packaging'].upload_package_to_gcs.assert_not_called()
            finally:
                Path(tmp.name).unlink(missing_ok=True)

    @patch('synapse_sdk.plugins.upload.download_file')
    def test_convert_https_to_ray_gcs(self, mock_download, mock_ray_module, mock_https_url, mock_gcs_uri):
        """Test that HTTPS URLs are also converted to Ray GCS."""
        # Arrange
        mock_ray_module['ray'].is_initialized.return_value = True
        mock_ray_module['packaging'].get_uri_for_package.return_value = mock_gcs_uri
        mock_ray_module['packaging'].package_exists.return_value = False

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(b'test zip content')
            tmp.flush()
            mock_download.return_value = tmp.name

            try:
                # Act
                from synapse_sdk.plugins.utils import convert_http_to_ray_gcs

                result = convert_http_to_ray_gcs(mock_https_url)

                # Assert
                assert result == mock_gcs_uri
                mock_download.assert_called_once()
                mock_ray_module['packaging'].upload_package_to_gcs.assert_called_once()
            finally:
                Path(tmp.name).unlink(missing_ok=True)

    def test_convert_http_to_ray_gcs_ray_not_installed(self, mock_http_url):
        """Test that RuntimeError is raised when Ray is not installed."""
        # Remove ray from sys.modules if it exists
        modules_to_remove = [k for k in sys.modules.keys() if k.startswith('ray')]
        original_modules = {k: sys.modules.pop(k) for k in modules_to_remove if k in sys.modules}

        try:
            # Force reload to trigger ImportError
            import importlib

            import synapse_sdk.plugins.utils.ray_gcs

            importlib.reload(synapse_sdk.plugins.utils.ray_gcs)

            # Act & Assert
            with pytest.raises(RuntimeError) as exc_info:
                synapse_sdk.plugins.utils.ray_gcs.convert_http_to_ray_gcs(mock_http_url)

            assert 'Ray is not installed' in str(exc_info.value)
            assert 'pip install ray' in str(exc_info.value)
        finally:
            # Restore original modules
            sys.modules.update(original_modules)

    def test_convert_http_to_ray_gcs_ray_not_initialized(self, mock_ray_module, mock_http_url):
        """Test that RuntimeError is raised when Ray is not initialized."""
        # Arrange
        mock_ray_module['ray'].is_initialized.return_value = False

        # Act & Assert
        from synapse_sdk.plugins.utils import convert_http_to_ray_gcs

        with pytest.raises(RuntimeError) as exc_info:
            convert_http_to_ray_gcs(mock_http_url)

        assert 'Ray must be initialized' in str(exc_info.value)
        assert 'ray.init()' in str(exc_info.value)

    @patch('synapse_sdk.plugins.upload.download_file')
    def test_convert_http_to_ray_gcs_download_fails(self, mock_download, mock_ray_module, mock_http_url):
        """Test that download errors propagate correctly."""
        # Arrange
        mock_ray_module['ray'].is_initialized.return_value = True
        mock_download.side_effect = Exception('Network error')

        # Act & Assert
        from synapse_sdk.plugins.utils import convert_http_to_ray_gcs

        with pytest.raises(Exception) as exc_info:
            convert_http_to_ray_gcs(mock_http_url)

        assert 'Network error' in str(exc_info.value)

    @patch('synapse_sdk.plugins.upload.download_file')
    def test_convert_http_to_ray_gcs_upload_fails(self, mock_download, mock_ray_module, mock_http_url, mock_gcs_uri):
        """Test that upload errors propagate correctly."""
        # Arrange
        mock_ray_module['ray'].is_initialized.return_value = True
        mock_ray_module['packaging'].get_uri_for_package.return_value = mock_gcs_uri
        mock_ray_module['packaging'].package_exists.return_value = False
        mock_ray_module['packaging'].upload_package_to_gcs.side_effect = Exception('GCS upload error')

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(b'test zip content')
            tmp.flush()
            mock_download.return_value = tmp.name

            try:
                # Act & Assert
                from synapse_sdk.plugins.utils import convert_http_to_ray_gcs

                with pytest.raises(Exception) as exc_info:
                    convert_http_to_ray_gcs(mock_http_url)

                assert 'GCS upload error' in str(exc_info.value)
            finally:
                Path(tmp.name).unlink(missing_ok=True)

    @patch('synapse_sdk.plugins.upload.download_file')
    def test_convert_http_to_ray_gcs_creates_temp_directory(
        self, mock_download, mock_ray_module, mock_http_url, mock_gcs_uri
    ):
        """Test that temporary directory is cleaned up after conversion."""
        # Arrange
        mock_ray_module['ray'].is_initialized.return_value = True
        mock_ray_module['packaging'].get_uri_for_package.return_value = mock_gcs_uri
        mock_ray_module['packaging'].package_exists.return_value = False

        # Track the temp directory path
        temp_dir_path = None

        def capture_temp_dir(url, path):
            nonlocal temp_dir_path
            temp_dir_path = path
            temp_file = Path(path) / 'downloaded.zip'
            temp_file.write_bytes(b'test content')
            return str(temp_file)

        mock_download.side_effect = capture_temp_dir

        # Act
        from synapse_sdk.plugins.utils import convert_http_to_ray_gcs

        result = convert_http_to_ray_gcs(mock_http_url)

        # Assert
        assert result == mock_gcs_uri
        # Temp directory should be cleaned up
        assert temp_dir_path is None or not Path(temp_dir_path).exists()

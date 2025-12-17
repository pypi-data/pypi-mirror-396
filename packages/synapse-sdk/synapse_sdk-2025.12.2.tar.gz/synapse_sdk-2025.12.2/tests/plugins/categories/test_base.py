"""Tests for Action.plugin_url property with HTTP → Ray GCS conversion."""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestActionPluginUrl:
    """Test suite for Action.plugin_url property."""

    @pytest.fixture
    def mock_action(self):
        """Create a mock Action instance."""
        action = Mock()
        action.debug = False
        action.plugin_release = Mock()
        action.plugin_storage_url = 'http://django.local/media/'
        action.envs = {}
        return action

    # Debug mode tests (existing behavior)

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_debug_https_ray_initialized(self, mock_convert, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH with https:// URL converts to GCS when Ray is initialized."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': 'https://example.com/plugin.zip'}
        mock_convert.return_value = 'gcs://_ray_pkg_https123.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = True
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'gcs://_ray_pkg_https123.zip'
            mock_convert.assert_called_once_with('https://example.com/plugin.zip')
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    def test_plugin_url_debug_https_ray_not_initialized(self, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH with https:// URL returns as-is when Ray not initialized."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': 'https://example.com/plugin.zip'}

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = False
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'https://example.com/plugin.zip'
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_debug_http_ray_initialized(self, mock_convert, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH with http:// URL converts to GCS when Ray is initialized."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': 'http://example.com/plugin.zip'}
        mock_convert.return_value = 'gcs://_ray_pkg_http123.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = True
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'gcs://_ray_pkg_http123.zip'
            mock_convert.assert_called_once_with('http://example.com/plugin.zip')
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    def test_plugin_url_debug_http_ray_not_initialized(self, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH with http:// URL returns as-is when Ray not initialized."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': 'http://example.com/plugin.zip'}

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = False
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'http://example.com/plugin.zip'
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    @patch('synapse_sdk.plugins.categories.base.archive_and_upload')
    def test_plugin_url_debug_local_path(self, mock_archive, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH with local path uploads when storage is configured."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {
            'SYNAPSE_DEBUG_PLUGIN_PATH': '/local/path/to/plugin',
            'SYNAPSE_PLUGIN_STORAGE': 's3://bucket/',
        }
        mock_action.plugin_storage_url = 's3://bucket/'
        mock_archive.return_value = 's3://bucket/archived.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://bucket/archived.zip'
        mock_archive.assert_called_once_with('/local/path/to/plugin', 's3://bucket/')

    @patch('synapse_sdk.plugins.categories.base.archive_and_upload')
    def test_plugin_url_debug_default_path(self, mock_archive, mock_action):
        """Test SYNAPSE_DEBUG_PLUGIN_PATH defaults to current directory and uploads when storage is configured."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_PLUGIN_STORAGE': 's3://bucket/'}  # Storage configured
        mock_action.plugin_storage_url = 's3://bucket/'
        mock_archive.return_value = 's3://bucket/archived.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://bucket/archived.zip'
        mock_archive.assert_called_once_with('.', 's3://bucket/')

    # Production mode tests (new behavior)

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_http_converts_to_gcs_when_ray_initialized(self, mock_convert, mock_action):
        """Test that HTTP URLs are converted to Ray GCS when Ray is initialized."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'http://django.local/media/plugins/abc123.zip'
        mock_convert.return_value = 'gcs://_ray_pkg_xyz789.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = True
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'gcs://_ray_pkg_xyz789.zip'
            mock_convert.assert_called_once_with('http://django.local/media/plugins/abc123.zip')
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    def test_plugin_url_production_http_no_convert_when_ray_not_initialized(self, mock_action):
        """Test that HTTP URLs are not converted when Ray is not initialized (job submission)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'http://django.local/media/plugins/abc123.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = False
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'http://django.local/media/plugins/abc123.zip'
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_https_converts_to_gcs_when_ray_initialized(self, mock_convert, mock_action):
        """Test that HTTPS URLs are converted to Ray GCS when Ray is initialized."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'https://django.local/media/plugins/abc123.zip'
        mock_convert.return_value = 'gcs://_ray_pkg_xyz789.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = True
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'gcs://_ray_pkg_xyz789.zip'
            mock_convert.assert_called_once_with('https://django.local/media/plugins/abc123.zip')
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    def test_plugin_url_production_https_no_convert_when_ray_not_initialized(self, mock_action):
        """Test that HTTPS URLs are not converted when Ray is not initialized (job submission)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'https://django.local/media/plugins/abc123.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = False
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'https://django.local/media/plugins/abc123.zip'
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_s3_no_conversion(self, mock_convert, mock_action):
        """Test that s3:// URLs are not converted (already Ray-compatible)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 's3://my-bucket/plugins/abc123.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://my-bucket/plugins/abc123.zip'
        mock_convert.assert_not_called()

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_gs_no_conversion(self, mock_convert, mock_action):
        """Test that gs:// URLs are not converted (already Ray-compatible)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'gs://my-bucket/plugins/abc123.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 'gs://my-bucket/plugins/abc123.zip'
        mock_convert.assert_not_called()

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_gcs_no_conversion(self, mock_convert, mock_action):
        """Test that gcs:// URLs are not converted (already Ray GCS format)."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'gcs://_ray_pkg_existing.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 'gcs://_ray_pkg_existing.zip'
        mock_convert.assert_not_called()

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_conversion_called_with_correct_url(self, mock_convert, mock_action):
        """Test that convert_http_to_ray_gcs is called with the exact URL from storage when Ray is initialized."""
        # Arrange
        expected_url = 'http://custom-domain.com/media/special/plugin-v2.0.zip'
        mock_action.plugin_release.get_url.return_value = expected_url
        mock_convert.return_value = 'gcs://_ray_pkg_custom.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = True
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'gcs://_ray_pkg_custom.zip'
            mock_convert.assert_called_once_with(expected_url)
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_multiple_calls_caching(self, mock_convert, mock_action):
        """Test that plugin_url can be called multiple times (property behavior) when Ray is initialized."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'http://django.local/media/plugins/test.zip'
        mock_convert.return_value = 'gcs://_ray_pkg_test.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = True
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url1 = Action.plugin_url.fget(mock_action)
            url2 = Action.plugin_url.fget(mock_action)

            # Assert
            assert url1 == 'gcs://_ray_pkg_test.zip'
            assert url2 == 'gcs://_ray_pkg_test.zip'
            # Should be called twice since it's a property, not cached
            assert mock_convert.call_count == 2
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_production_conversion_error_fallback(self, mock_convert, mock_action):
        """Test that errors from convert_http_to_ray_gcs fall back to HTTP URL."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 'http://django.local/media/plugins/test.zip'
        mock_convert.side_effect = RuntimeError('Ray not initialized')

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert - should fall back to HTTP URL instead of raising
        assert url == 'http://django.local/media/plugins/test.zip'

    def test_plugin_url_production_calls_get_url_with_storage_url(self, mock_action):
        """Test that plugin_release.get_url is called with plugin_storage_url."""
        # Arrange
        mock_action.plugin_release.get_url.return_value = 's3://bucket/plugin.zip'
        expected_storage_url = 'http://custom-storage.local/path/'
        mock_action.plugin_storage_url = expected_storage_url

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://bucket/plugin.zip'
        mock_action.plugin_release.get_url.assert_called_once_with(expected_storage_url)

    # Tests for SYNAPSE_PLUGIN_STORAGE being optional

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_debug_http_no_storage_converts_when_ray_init(self, mock_convert, mock_action):
        """Test that HTTP URLs in debug mode convert to GCS when Ray is initialized (no storage needed)."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': 'http://example.com/plugin.zip'}
        # No SYNAPSE_PLUGIN_STORAGE set
        mock_convert.return_value = 'gcs://_ray_pkg_xyz789.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = True
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'gcs://_ray_pkg_xyz789.zip'
            mock_convert.assert_called_once_with('http://example.com/plugin.zip')
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    @patch('synapse_sdk.plugins.utils.convert_http_to_ray_gcs')
    def test_plugin_url_debug_https_no_storage_converts_when_ray_init(self, mock_convert, mock_action):
        """Test that HTTPS URLs in debug mode convert to GCS when Ray is initialized (no storage needed)."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': 'https://example.com/plugin.zip'}
        # No SYNAPSE_PLUGIN_STORAGE set
        mock_convert.return_value = 'gcs://_ray_pkg_abc123.zip'

        # Mock ray module
        mock_ray = MagicMock()
        mock_ray.is_initialized.return_value = True
        sys.modules['ray'] = mock_ray

        try:
            # Act
            from synapse_sdk.plugins.categories.base import Action

            url = Action.plugin_url.fget(mock_action)

            # Assert
            assert url == 'gcs://_ray_pkg_abc123.zip'
            mock_convert.assert_called_once_with('https://example.com/plugin.zip')
        finally:
            # Clean up
            if 'ray' in sys.modules:
                del sys.modules['ray']

    def test_plugin_url_debug_local_path_no_storage(self, mock_action):
        """Test that local paths in debug mode return as-is when SYNAPSE_PLUGIN_STORAGE is not set."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {'SYNAPSE_DEBUG_PLUGIN_PATH': '/local/path/to/plugin'}
        # No SYNAPSE_PLUGIN_STORAGE set

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == '/local/path/to/plugin'

    def test_plugin_url_debug_default_path_no_storage(self, mock_action):
        """Test that default path (.) in debug mode returns as-is when SYNAPSE_PLUGIN_STORAGE is not set."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {}  # No SYNAPSE_DEBUG_PLUGIN_PATH and no SYNAPSE_PLUGIN_STORAGE

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == '.'

    @patch('synapse_sdk.plugins.categories.base.archive_and_upload')
    def test_plugin_url_debug_local_path_with_storage_uploads(self, mock_archive, mock_action):
        """Test that local paths in debug mode are uploaded when SYNAPSE_PLUGIN_STORAGE is set."""
        # Arrange
        mock_action.debug = True
        mock_action.envs = {
            'SYNAPSE_DEBUG_PLUGIN_PATH': '/local/path/to/plugin',
            'SYNAPSE_PLUGIN_STORAGE': 's3://bucket/',
        }
        mock_action.plugin_storage_url = 's3://bucket/'
        mock_archive.return_value = 's3://bucket/archived.zip'

        # Act
        from synapse_sdk.plugins.categories.base import Action

        url = Action.plugin_url.fget(mock_action)

        # Assert
        assert url == 's3://bucket/archived.zip'
        mock_archive.assert_called_once_with('/local/path/to/plugin', 's3://bucket/')

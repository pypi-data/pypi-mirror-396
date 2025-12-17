"""Shared fixtures for plugin utils tests."""

import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def mock_ray_initialized():
    """Mock ray module with is_initialized() returning True."""
    with pytest.importorskip('ray', reason='Ray is not installed'):
        import ray

        original_is_initialized = ray.is_initialized

        def mock_is_init():
            return True

        ray.is_initialized = mock_is_init
        yield ray
        ray.is_initialized = original_is_initialized


@pytest.fixture
def mock_ray_not_initialized():
    """Mock ray.is_initialized() returning False."""
    mock_ray = MagicMock()
    mock_ray.is_initialized.return_value = False
    return mock_ray


@pytest.fixture
def mock_ray_packaging_functions():
    """Mock Ray's packaging functions for GCS upload."""
    mocks = {
        'get_uri_for_package': Mock(return_value='gcs://_ray_pkg_test123.zip'),
        'package_exists': Mock(return_value=False),
        'upload_package_to_gcs': Mock(),
    }
    return mocks


@pytest.fixture
def mock_downloaded_zip_file():
    """Create a real temporary zip file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / 'test_plugin.zip'

        # Create a zip file with some content
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('plugin.yaml', 'name: Test Plugin\nversion: 1.0.0\n')
            zf.writestr('main.py', 'print("Hello from plugin")\n')

        yield str(zip_path)


@pytest.fixture
def mock_http_url():
    """Return a test HTTP URL."""
    return 'http://django.local/media/plugins/test_plugin.zip'


@pytest.fixture
def mock_https_url():
    """Return a test HTTPS URL."""
    return 'https://django.local/media/plugins/test_plugin.zip'


@pytest.fixture
def mock_gcs_uri():
    """Return a test gcs:// URI."""
    return 'gcs://_ray_pkg_abc123def456.zip'


@pytest.fixture
def mock_s3_uri():
    """Return a test s3:// URI."""
    return 's3://my-bucket/plugins/test_plugin.zip'


@pytest.fixture
def mock_gs_uri():
    """Return a test gs:// URI."""
    return 'gs://my-bucket/plugins/test_plugin.zip'

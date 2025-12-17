"""Utilities for converting HTTP URLs to Ray GCS URLs."""

import tempfile
from pathlib import Path


def convert_http_to_ray_gcs(http_url: str) -> str:
    """Convert HTTP URL to Ray GCS URL by downloading and uploading to Ray's GCS.

    Ray's working_dir only accepts certain protocols (gcs://, s3://, gs://, https://).
    When SYNAPSE_PLUGIN_STORAGE is an HTTP URL (Django media server), this function
    converts it to a Ray-compatible gcs:// URL by:
    1. Downloading the file from HTTP
    2. Uploading it to Ray's Global Control Store (GCS)
    3. Returning the content-addressable gcs:// URI

    Args:
        http_url: HTTP/HTTPS URL to plugin zip file

    Returns:
        gcs:// URL that Ray can use for working_dir
        Example: "gcs://_ray_pkg_abc123def456.zip"

    Raises:
        RuntimeError: If Ray is not initialized or not installed
        requests.exceptions.RequestException: If HTTP download fails

    Note:
        - Ray must be initialized (ray.init()) before calling this function
        - The gcs:// URI is content-addressable (same file = same URI)
        - Ray automatically deduplicates uploads via package_exists()
    """
    try:
        import ray
    except ImportError:
        raise RuntimeError(
            'Ray is not installed but is required for HTTP → GCS conversion. Install ray with: pip install ray'
        )

    if not ray.is_initialized():
        raise RuntimeError(
            'Ray must be initialized before converting HTTP URLs to GCS. '
            'Call ray.init() before submitting jobs with HTTP storage.'
        )

    from ray._private.runtime_env.packaging import (
        get_uri_for_package,
        package_exists,
        upload_package_to_gcs,
    )

    from synapse_sdk.plugins.upload import download_file

    # Download HTTP file to temporary location
    with tempfile.TemporaryDirectory() as temp_dir:
        local_path = Path(download_file(http_url, temp_dir))

        # Generate content-addressable gcs:// URI based on file content
        gcs_uri = get_uri_for_package(local_path)

        # Check if already exists in Ray GCS (deduplication)
        if not package_exists(gcs_uri):
            # Upload to Ray's Global Control Store
            upload_package_to_gcs(gcs_uri, local_path.read_bytes())

        return gcs_uri

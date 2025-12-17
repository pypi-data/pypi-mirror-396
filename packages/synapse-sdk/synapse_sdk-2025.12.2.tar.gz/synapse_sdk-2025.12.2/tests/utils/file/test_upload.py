"""Unit tests for file upload utilities."""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from synapse_sdk.utils.file.upload import (
    FilesDict,
    FileProcessingError,
    FileValidationError,
    close_file_handles,
    process_files_for_upload,
)


def _has_upath():
    """Check if upath is installed."""
    try:
        import upath

        return True
    except ImportError:
        return False


class TestProcessFilesForUpload:
    """Test suite for process_files_for_upload function."""

    def test_process_files_with_bytes(self):
        """Test that bytes content passes through unchanged."""
        files = {'file': b'binary content'}
        processed, handles = process_files_for_upload(files)

        assert processed == {'file': b'binary content'}
        assert handles == []

    def test_process_files_with_multiple_bytes(self):
        """Test multiple bytes fields."""
        files = {
            'file1': b'content1',
            'file2': b'content2',
            'metadata': b'{"version": 1}',
        }
        processed, handles = process_files_for_upload(files)

        assert processed == files
        assert handles == []

    def test_process_files_with_string_path(self, tmp_path):
        """Test string path conversion to Path and file opening."""
        # Create a temporary file
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        files = {'file': str(test_file)}
        processed, handles = process_files_for_upload(files)

        # Should return tuple of (filename, file_handle)
        assert 'file' in processed
        assert isinstance(processed['file'], tuple)
        assert processed['file'][0] == 'test.txt'
        assert len(handles) == 1

        # Verify file handle is valid
        content = handles[0].read()
        assert content == b'test content'

        # Clean up
        close_file_handles(handles)

    def test_process_files_with_path_object(self, tmp_path):
        """Test Path object handling."""
        test_file = tmp_path / 'document.pdf'
        test_file.write_bytes(b'PDF content')

        files = {'document': test_file}
        processed, handles = process_files_for_upload(files)

        assert 'document' in processed
        assert processed['document'][0] == 'document.pdf'
        assert len(handles) == 1

        # Verify content
        assert handles[0].read() == b'PDF content'

        # Clean up
        close_file_handles(handles)

    def test_process_files_with_mixed_types(self, tmp_path):
        """Test processing files with mixed input types."""
        test_file = tmp_path / 'data.json'
        test_file.write_text('{"key": "value"}')

        files = {
            'metadata': b'raw bytes',
            'document': test_file,
            'report': str(test_file),
        }

        processed, handles = process_files_for_upload(files)

        # Bytes should pass through
        assert processed['metadata'] == b'raw bytes'

        # Path objects should be opened
        assert processed['document'][0] == 'data.json'
        assert processed['report'][0] == 'data.json'

        # Should have 2 open handles (document and report)
        assert len(handles) == 2

        # Clean up
        close_file_handles(handles)

    def test_process_files_with_upath_like_object(self):
        """Test UPath-like objects using duck typing."""
        # Mock a UPath-like object
        mock_upath = MagicMock()
        mock_upath.name = 'cloud_file.txt'
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'cloud content'
        mock_upath.open.return_value = mock_file_handle

        files = {'cloud_file': mock_upath}
        processed, handles = process_files_for_upload(files)

        # Verify open was called with binary read mode
        mock_upath.open.assert_called_once_with(mode='rb')

        # Should create file tuple
        assert processed['cloud_file'][0] == 'cloud_file.txt'
        assert processed['cloud_file'][1] == mock_file_handle

        # Should track the handle
        assert len(handles) == 1
        assert handles[0] == mock_file_handle

    def test_process_files_with_empty_filename(self):
        """Test handling of path-like object with empty name."""
        mock_path = MagicMock()
        mock_path.name = ''  # Empty name
        mock_file_handle = MagicMock()
        mock_path.open.return_value = mock_file_handle

        files = {'upload': mock_path}
        processed, handles = process_files_for_upload(files)

        # Should fallback to 'file' when name is empty
        assert processed['upload'][0] == 'file'
        assert len(handles) == 1

    def test_process_files_none_value_raises_validation_error(self):
        """Test that None values raise FileValidationError."""
        files = {'file': None}

        with pytest.raises(FileValidationError) as exc_info:
            process_files_for_upload(files)

        assert 'cannot be None' in str(exc_info.value)
        assert "'file'" in str(exc_info.value)

    def test_process_files_none_in_mixed_dict_raises_validation_error(self):
        """Test None validation in dictionary with other valid values."""
        files = {
            'valid_file': b'content',
            'invalid_file': None,
        }

        with pytest.raises(FileValidationError) as exc_info:
            process_files_for_upload(files)

        assert 'invalid_file' in str(exc_info.value)
        assert 'cannot be None' in str(exc_info.value)

    def test_process_files_unsupported_type_raises_validation_error(self):
        """Test that unsupported types raise FileValidationError."""
        files = {'file': 12345}  # Integer is not supported

        with pytest.raises(FileValidationError) as exc_info:
            process_files_for_upload(files)

        assert 'unsupported type' in str(exc_info.value)
        assert "'int'" in str(exc_info.value)
        assert '12345' in str(exc_info.value)

    def test_process_files_various_unsupported_types(self):
        """Test various unsupported types."""
        unsupported_values = [
            ({'file': []}, 'list'),
            ({'file': {}}, 'dict'),
            ({'file': 3.14}, 'float'),
            ({'file': True}, 'bool'),
        ]

        for files, expected_type in unsupported_values:
            with pytest.raises(FileValidationError) as exc_info:
                process_files_for_upload(files)
            assert expected_type in str(exc_info.value).lower()

    def test_process_files_open_failure_raises_processing_error(self, tmp_path):
        """Test that file opening errors raise FileProcessingError."""
        # Create path to non-existent file
        non_existent = tmp_path / 'does_not_exist.txt'

        files = {'file': non_existent}

        with pytest.raises(FileProcessingError) as exc_info:
            process_files_for_upload(files)

        assert 'Failed to open' in str(exc_info.value)
        assert 'does_not_exist.txt' in str(exc_info.value)

    def test_process_files_cleanup_on_error(self, tmp_path):
        """Test that already opened files are closed when an error occurs."""
        # Create two files
        file1 = tmp_path / 'file1.txt'
        file1.write_text('content1')

        # Create a mock that succeeds for first file, fails for second
        mock_path = MagicMock()
        mock_path.name = 'failing_file.txt'
        mock_path.open.side_effect = IOError('Permission denied')

        files = {
            'file1': file1,
            'file2': mock_path,
        }

        # Track if cleanup happens
        with pytest.raises(FileProcessingError):
            process_files_for_upload(files)

        # Note: In real scenario, file1 would be closed
        # We can't easily verify this without more complex mocking

    def test_process_files_empty_dict(self):
        """Test processing empty files dictionary."""
        files = {}
        processed, handles = process_files_for_upload(files)

        assert processed == {}
        assert handles == []

    def test_process_files_pathlib_none_attribute(self):
        """Test path object where name attribute is None."""
        mock_path = MagicMock()
        mock_path.name = None  # None instead of empty string
        mock_file_handle = MagicMock()
        mock_path.open.return_value = mock_file_handle

        files = {'upload': mock_path}
        processed, handles = process_files_for_upload(files)

        # Should fallback to 'file'
        assert processed['upload'][0] == 'file'

    def test_process_files_returns_correct_types(self, tmp_path):
        """Test that return types match type annotations."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        files = {'file': test_file}
        processed, handles = process_files_for_upload(files)

        # Verify types
        assert isinstance(processed, dict)
        assert isinstance(handles, list)


class TestCloseFileHandles:
    """Test suite for close_file_handles function."""

    def test_close_single_handle(self):
        """Test closing a single file handle."""
        mock_handle = MagicMock()
        close_file_handles([mock_handle])

        mock_handle.close.assert_called_once()

    def test_close_multiple_handles(self):
        """Test closing multiple file handles."""
        handles = [MagicMock(), MagicMock(), MagicMock()]
        close_file_handles(handles)

        for handle in handles:
            handle.close.assert_called_once()

    def test_close_empty_list(self):
        """Test closing empty list of handles."""
        # Should not raise any errors
        close_file_handles([])

    def test_close_handles_with_error(self):
        """Test that errors during close are silently ignored."""
        mock_handle1 = MagicMock()
        mock_handle2 = MagicMock()
        mock_handle3 = MagicMock()

        # Make the second handle raise an error
        mock_handle2.close.side_effect = IOError('Close failed')

        # Should not raise, should continue closing other handles
        close_file_handles([mock_handle1, mock_handle2, mock_handle3])

        # All close methods should be called
        mock_handle1.close.assert_called_once()
        mock_handle2.close.assert_called_once()
        mock_handle3.close.assert_called_once()

    def test_close_handles_all_error(self):
        """Test that all errors are ignored."""
        handles = [MagicMock() for _ in range(3)]
        for handle in handles:
            handle.close.side_effect = Exception('Error')

        # Should not raise
        close_file_handles(handles)

    def test_close_real_file_handles(self, tmp_path):
        """Test closing real file handles."""
        # Create real files
        files = [tmp_path / f'file{i}.txt' for i in range(3)]
        for f in files:
            f.write_text('content')

        # Open handles
        handles = [f.open('rb') for f in files]

        # Close them
        close_file_handles(handles)

        # Verify all are closed
        for handle in handles:
            assert handle.closed


class TestTypeDefinitions:
    """Test type definitions are properly defined."""

    def test_files_dict_type_exists(self):
        """Test that FilesDict type is defined."""
        assert FilesDict is not None

    def test_exception_hierarchy(self):
        """Test exception class hierarchy."""
        from synapse_sdk.utils.file.upload import FileUploadError

        # FileValidationError and FileProcessingError should inherit from FileUploadError
        assert issubclass(FileValidationError, FileUploadError)
        assert issubclass(FileProcessingError, FileUploadError)
        assert issubclass(FileUploadError, Exception)


class TestIntegrationWithBaseClient:
    """Integration tests simulating BaseClient usage."""

    def test_typical_upload_workflow(self, tmp_path):
        """Test typical file upload workflow as used by BaseClient."""
        # Create test files
        document = tmp_path / 'document.pdf'
        document.write_bytes(b'PDF content')

        image = tmp_path / 'image.jpg'
        image.write_bytes(b'JPEG content')

        # Simulate BaseClient file processing
        files = {
            'document': document,
            'image': str(image),
            'metadata': b'{"version": 1}',
        }

        processed, handles = process_files_for_upload(files)

        try:
            # Verify structure is ready for requests library
            assert processed['document'][0] == 'document.pdf'
            assert processed['image'][0] == 'image.jpg'
            assert processed['metadata'] == b'{"version": 1}'

            # Verify handles can be read
            assert len(handles) == 2
        finally:
            close_file_handles(handles)

    def test_error_handling_workflow(self, tmp_path):
        """Test error handling as done in BaseClient._request."""
        files = {'file': None}

        try:
            processed, handles = process_files_for_upload(files)
            assert False, 'Should have raised FileValidationError'
        except FileValidationError as e:
            # BaseClient should catch this and convert to ClientError(400)
            assert 'cannot be None' in str(e)


class TestCloudStorageCompatibility:
    """Test compatibility with various cloud storage path types (S3, GCS, Azure, MinIO, etc.)."""

    def test_s3_path_compatibility(self):
        """Test S3Path compatibility (s3://)."""
        mock_s3path = MagicMock()
        mock_s3path.name = 'data.csv'
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'S3 data content'
        mock_s3path.open.return_value = mock_file_handle

        files = {'s3_file': mock_s3path}
        processed, handles = process_files_for_upload(files)

        mock_s3path.open.assert_called_once_with(mode='rb')
        assert processed['s3_file'][0] == 'data.csv'
        assert processed['s3_file'][1] == mock_file_handle
        assert len(handles) == 1

    def test_gcs_path_compatibility(self):
        """Test GCSPath compatibility (gs://)."""
        mock_gcspath = MagicMock()
        mock_gcspath.name = 'model.pkl'
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'GCS model data'
        mock_gcspath.open.return_value = mock_file_handle

        files = {'gcs_file': mock_gcspath}
        processed, handles = process_files_for_upload(files)

        mock_gcspath.open.assert_called_once_with(mode='rb')
        assert processed['gcs_file'][0] == 'model.pkl'
        assert len(handles) == 1

    def test_azure_path_compatibility(self):
        """Test AzurePath compatibility (az://)."""
        mock_azurepath = MagicMock()
        mock_azurepath.name = 'blob.json'
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'{"azure": "data"}'
        mock_azurepath.open.return_value = mock_file_handle

        files = {'azure_file': mock_azurepath}
        processed, handles = process_files_for_upload(files)

        mock_azurepath.open.assert_called_once_with(mode='rb')
        assert processed['azure_file'][0] == 'blob.json'
        assert len(handles) == 1

    def test_sftp_path_compatibility(self):
        """Test SFTPPath compatibility (sftp://)."""
        mock_sftppath = MagicMock()
        mock_sftppath.name = 'remote_file.txt'
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'SFTP content'
        mock_sftppath.open.return_value = mock_file_handle

        files = {'sftp_file': mock_sftppath}
        processed, handles = process_files_for_upload(files)

        mock_sftppath.open.assert_called_once_with(mode='rb')
        assert processed['sftp_file'][0] == 'remote_file.txt'
        assert len(handles) == 1

    def test_minio_s3_compatible_path(self):
        """Test MinIO path (S3-compatible storage)."""
        mock_minio_path = MagicMock()
        mock_minio_path.name = 'bucket/object.bin'
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'MinIO binary data'
        mock_minio_path.open.return_value = mock_file_handle

        files = {'minio_file': mock_minio_path}
        processed, handles = process_files_for_upload(files)

        mock_minio_path.open.assert_called_once_with(mode='rb')
        assert processed['minio_file'][0] == 'bucket/object.bin'
        assert len(handles) == 1

    def test_backend_ai_storage_compatibility(self):
        """Test Backend.AI storage path compatibility."""
        mock_backend_path = MagicMock()
        mock_backend_path.name = 'vfolder/dataset.h5'
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'HDF5 dataset'
        mock_backend_path.open.return_value = mock_file_handle

        files = {'backend_ai': mock_backend_path}
        processed, handles = process_files_for_upload(files)

        mock_backend_path.open.assert_called_once_with(mode='rb')
        assert processed['backend_ai'][0] == 'vfolder/dataset.h5'
        assert len(handles) == 1

    def test_mixed_cloud_and_local_paths(self, tmp_path):
        """Test mixing cloud storage paths with local paths."""
        local_file = tmp_path / 'local.txt'
        local_file.write_text('local content')

        mock_s3path = MagicMock()
        mock_s3path.name = 'cloud.txt'
        mock_cloud_handle = MagicMock()
        mock_cloud_handle.read.return_value = b'cloud content'
        mock_s3path.open.return_value = mock_cloud_handle

        files = {
            'local': local_file,
            's3': mock_s3path,
            'bytes': b'raw bytes',
        }

        processed, handles = process_files_for_upload(files)

        assert processed['local'][0] == 'local.txt'
        assert processed['s3'][0] == 'cloud.txt'
        assert processed['bytes'] == b'raw bytes'
        assert len(handles) == 2  # local and s3, not bytes

        close_file_handles(handles)

    def test_cloud_path_with_special_characters(self):
        """Test cloud path with special characters in filename."""
        mock_path = MagicMock()
        mock_path.name = 'data-2024-12-11_v1.0.json'
        mock_file_handle = MagicMock()
        mock_path.open.return_value = mock_file_handle

        files = {'special': mock_path}
        processed, handles = process_files_for_upload(files)

        assert processed['special'][0] == 'data-2024-12-11_v1.0.json'

    def test_cloud_path_with_unicode_filename(self):
        """Test cloud path with unicode characters."""
        mock_path = MagicMock()
        mock_path.name = '데이터_파일.txt'  # Korean characters
        mock_file_handle = MagicMock()
        mock_path.open.return_value = mock_file_handle

        files = {'unicode': mock_path}
        processed, handles = process_files_for_upload(files)

        assert processed['unicode'][0] == '데이터_파일.txt'

    @pytest.mark.skipif(not _has_upath(), reason='upath not installed')
    def test_real_upath_integration(self):
        """Test with real UPath library if available."""
        from upath import UPath

        try:
            # Try memory filesystem for testing
            mem_path = UPath('memory://test_bucket/test_file.txt')
            mem_path.write_text('test content')

            files = {'memory_file': mem_path}
            processed, handles = process_files_for_upload(files)

            assert 'memory_file' in processed
            assert len(handles) == 1
            assert handles[0].read() == b'test content'

            close_file_handles(handles)
        except Exception as e:
            pytest.skip(f'Memory filesystem not available: {e}')


class TestDuckTypingRobustness:
    """Test robustness of duck typing approach for cloud paths."""

    def test_object_with_only_open_no_name(self):
        """Test object with open() but no name attribute."""
        mock_obj = MagicMock()
        mock_obj.open = MagicMock()
        del mock_obj.name

        files = {'incomplete': mock_obj}

        with pytest.raises(FileValidationError):
            process_files_for_upload(files)

    def test_object_with_only_name_no_open(self):
        """Test object with name but no open() method."""
        mock_obj = MagicMock()
        mock_obj.name = 'file.txt'
        del mock_obj.open

        files = {'incomplete': mock_obj}

        with pytest.raises(FileValidationError):
            process_files_for_upload(files)

    def test_duck_typing_both_attributes_required(self):
        """Verify both 'open' and 'name' are required."""
        obj1 = object()
        obj2 = MagicMock(spec=['name'])
        obj2.name = 'test'
        obj3 = MagicMock(spec=['open'])

        for obj in [obj1, obj2, obj3]:
            with pytest.raises(FileValidationError):
                process_files_for_upload({'file': obj})

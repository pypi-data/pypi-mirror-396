"""
Tests for file chunking utilities.
"""

from unittest.mock import Mock, mock_open, patch

import pytest

from synapse_sdk.utils.file.chunking import read_file_in_chunks


class TestFileChunking:
    """Test file chunking utilities."""

    def test_read_small_file_single_chunk(self, tmp_path):
        """Test reading a small file that fits in a single chunk."""
        test_file = tmp_path / 'small_file.txt'
        test_content = b'Hello, world!'
        test_file.write_bytes(test_content)

        chunks = list(read_file_in_chunks(str(test_file)))

        assert len(chunks) == 1
        assert chunks[0] == test_content

    def test_read_large_file_multiple_chunks(self, tmp_path):
        """Test reading a large file that requires multiple chunks."""
        test_file = tmp_path / 'large_file.bin'
        chunk_size = 100  # Small chunk size for testing
        test_content = b'A' * 250  # Content that will span 3 chunks
        test_file.write_bytes(test_content)

        chunks = list(read_file_in_chunks(str(test_file), chunk_size=chunk_size))

        assert len(chunks) == 3
        assert chunks[0] == b'A' * 100
        assert chunks[1] == b'A' * 100
        assert chunks[2] == b'A' * 50

    def test_read_empty_file(self, tmp_path):
        """Test reading an empty file."""
        test_file = tmp_path / 'empty_file.txt'
        test_file.write_bytes(b'')

        chunks = list(read_file_in_chunks(str(test_file)))

        assert len(chunks) == 0

    def test_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError):
            list(read_file_in_chunks('/non/existent/file.txt'))

    def test_permission_error(self):
        """Test that PermissionError is properly propagated."""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = PermissionError('Permission denied')

            with pytest.raises(PermissionError):
                list(read_file_in_chunks('/some/file.txt'))

    def test_custom_chunk_size(self, tmp_path):
        """Test reading with custom chunk sizes."""
        test_file = tmp_path / 'custom_chunk_test.bin'
        test_content = b'B' * 1000
        test_file.write_bytes(test_content)

        # Test with different chunk sizes
        chunk_sizes = [50, 200, 333, 1500]

        for chunk_size in chunk_sizes:
            chunks = list(read_file_in_chunks(str(test_file), chunk_size=chunk_size))
            reconstructed = b''.join(chunks)

            assert reconstructed == test_content
            if chunk_size >= 1000:
                assert len(chunks) == 1
            else:
                assert len(chunks) == (1000 + chunk_size - 1) // chunk_size  # Ceiling division

    def test_binary_file_reading(self, tmp_path):
        """Test reading binary files with various byte patterns."""
        test_file = tmp_path / 'binary_file.bin'
        # Create binary content with various byte values
        test_content = bytes(range(256)) * 4  # 1024 bytes with all possible byte values
        test_file.write_bytes(test_content)

        chunks = list(read_file_in_chunks(str(test_file), chunk_size=500))
        reconstructed = b''.join(chunks)

        assert reconstructed == test_content
        assert len(chunks) == 3  # 1024 bytes in 500-byte chunks = 3 chunks

    def test_path_object_input(self, tmp_path):
        """Test that Path objects work as input."""
        test_file = tmp_path / 'path_object_test.txt'
        test_content = b'Testing Path object input'
        test_file.write_bytes(test_content)

        # Test with Path object
        chunks = list(read_file_in_chunks(test_file))

        assert len(chunks) == 1
        assert chunks[0] == test_content

    def test_default_chunk_size(self):
        """Test that the default chunk size is 50MB."""
        test_content = b'Test default chunk size'

        with patch('builtins.open', mock_open()) as mock_file:
            mock_file_handle = Mock()
            # First call returns content, second call returns empty (EOF)
            mock_file_handle.read.side_effect = [test_content, b'']
            mock_file.return_value.__enter__.return_value = mock_file_handle

            # Convert generator to list to trigger the read
            chunks = list(read_file_in_chunks('dummy_file.txt'))

            # Verify the default chunk size was used (50MB = 1024 * 1024 * 50)
            expected_chunk_size = 1024 * 1024 * 50
            mock_file_handle.read.assert_called_with(expected_chunk_size)

            # Verify we got the expected content
            assert len(chunks) == 1
            assert chunks[0] == test_content

    def test_file_integrity_with_chunks(self, tmp_path):
        """Test that file content integrity is maintained across chunks."""
        test_file = tmp_path / 'integrity_test.bin'

        # Create content with a known pattern
        original_content = b''
        for i in range(1000):
            original_content += f'Line {i:04d} - Some test content\n'.encode()

        test_file.write_bytes(original_content)

        # Read with various chunk sizes and verify content integrity
        for chunk_size in [1024, 4096, 16384]:
            chunks = list(read_file_in_chunks(str(test_file), chunk_size=chunk_size))
            reconstructed = b''.join(chunks)

            assert reconstructed == original_content
            assert len(reconstructed) == len(original_content)

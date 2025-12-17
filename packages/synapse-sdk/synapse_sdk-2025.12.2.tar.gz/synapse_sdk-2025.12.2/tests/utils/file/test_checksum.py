"""
Tests for file checksum utilities.
"""

import hashlib
from io import BytesIO, StringIO
from unittest.mock import Mock

from synapse_sdk.utils.file.checksum import get_checksum_from_file


class TestChecksumFromFile:
    """Test checksum calculation from file-like objects."""

    def test_bytesio_default_sha1(self):
        """Test checksum calculation with BytesIO using default SHA1."""
        test_data = b'Hello, world!'
        file_obj = BytesIO(test_data)

        checksum = get_checksum_from_file(file_obj)

        # Verify against expected SHA1
        expected = hashlib.sha1(test_data).hexdigest()
        assert checksum == expected

    def test_bytesio_custom_hash_algorithm(self):
        """Test checksum with different hash algorithms."""
        test_data = b'Test data for hashing'

        algorithms = [
            (hashlib.md5, hashlib.md5(test_data).hexdigest()),
            (hashlib.sha1, hashlib.sha1(test_data).hexdigest()),
            (hashlib.sha256, hashlib.sha256(test_data).hexdigest()),
        ]

        for algo, expected in algorithms:
            file_obj = BytesIO(test_data)
            checksum = get_checksum_from_file(file_obj, digest_mod=algo)
            assert checksum == expected

    def test_stringio_text_handling(self):
        """Test handling of StringIO (text) objects."""
        test_text = 'Hello, world!'
        file_obj = StringIO(test_text)

        checksum = get_checksum_from_file(file_obj)

        # Should match SHA1 of UTF-8 encoded text
        expected = hashlib.sha1(test_text.encode('utf-8')).hexdigest()
        assert checksum == expected

    def test_empty_file(self):
        """Test checksum of empty file."""
        empty_file = BytesIO(b'')

        checksum = get_checksum_from_file(empty_file)

        # SHA1 of empty bytes
        expected = hashlib.sha1(b'').hexdigest()
        assert checksum == expected

    def test_large_file_chunked_reading(self):
        """Test that large files are processed in chunks correctly."""
        # Create large test data (larger than chunk size of 4096)
        large_data = b'A' * 10000
        file_obj = BytesIO(large_data)

        checksum = get_checksum_from_file(file_obj)

        # Verify against expected checksum
        expected = hashlib.sha1(large_data).hexdigest()
        assert checksum == expected

    def test_file_pointer_reset(self):
        """Test that file pointer is reset to beginning if seek is available."""
        test_data = b'Test data'
        file_obj = BytesIO(test_data)

        # Move file pointer to middle
        file_obj.read(4)
        assert file_obj.tell() == 4

        # Calculate checksum should reset pointer and read full content
        checksum = get_checksum_from_file(file_obj)

        expected = hashlib.sha1(test_data).hexdigest()
        assert checksum == expected

    def test_file_without_seek_method(self):
        """Test handling of file objects without seek method."""
        test_data = b'Test without seek'

        # Create mock file object without seek method
        mock_file = Mock()
        mock_file.read.side_effect = [test_data[:4], test_data[4:8], test_data[8:], b'']
        # Ensure hasattr returns False for seek
        del mock_file.seek

        checksum = get_checksum_from_file(mock_file)

        expected = hashlib.sha1(test_data).hexdigest()
        assert checksum == expected

    def test_binary_content_integrity(self):
        """Test checksum with various binary content patterns."""
        # Test with all possible byte values
        binary_data = bytes(range(256))
        file_obj = BytesIO(binary_data)

        checksum = get_checksum_from_file(file_obj)

        expected = hashlib.sha1(binary_data).hexdigest()
        assert checksum == expected

    def test_consistent_results_multiple_calls(self):
        """Test that multiple calls on same file return same checksum."""
        test_data = b'Consistency test data'

        checksums = []
        for _ in range(3):
            file_obj = BytesIO(test_data)
            checksum = get_checksum_from_file(file_obj)
            checksums.append(checksum)

        # All checksums should be identical
        assert len(set(checksums)) == 1
        assert checksums[0] == hashlib.sha1(test_data).hexdigest()

    def test_real_file_object(self, tmp_path):
        """Test with actual file objects from filesystem."""
        test_file = tmp_path / 'test_checksum.txt'
        test_content = b'File system test content'
        test_file.write_bytes(test_content)

        with open(test_file, 'rb') as f:
            checksum = get_checksum_from_file(f)

        expected = hashlib.sha1(test_content).hexdigest()
        assert checksum == expected

    def test_unicode_text_encoding(self):
        """Test handling of Unicode text in StringIO."""
        unicode_text = 'Hello, 世界! 🌍'
        file_obj = StringIO(unicode_text)

        checksum = get_checksum_from_file(file_obj)

        # Should match SHA1 of UTF-8 encoded Unicode text
        expected = hashlib.sha1(unicode_text.encode('utf-8')).hexdigest()
        assert checksum == expected

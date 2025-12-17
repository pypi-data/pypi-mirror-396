import hashlib
from typing import IO, Any, Callable


def calculate_checksum(file_path, prefix=''):
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            md5_hash.update(byte_block)
    checksum = md5_hash.hexdigest()
    if prefix:
        return f'dev-{checksum}'
    return checksum


def get_checksum_from_file(file: IO[Any], digest_mod: Callable[[], Any] = hashlib.sha1) -> str:
    """
    Calculate checksum for a file-like object.

    Args:
        file (IO[Any]): File-like object with read() method that supports reading in chunks
        digest_mod (Callable[[], Any]): Hash algorithm from hashlib (defaults to hashlib.sha1)

    Returns:
        str: Hexadecimal digest of the file contents

    Example:
        ```python
        import hashlib
        from io import BytesIO
        from synapse_sdk.utils.file import get_checksum_from_file

        # With BytesIO
        data = BytesIO(b'Hello, world!')
        checksum = get_checksum_from_file(data)

        # With different hash algorithm
        checksum = get_checksum_from_file(data, digest_mod=hashlib.sha256)
        ```
    """
    digest = digest_mod()
    chunk_size = 4096

    # Reset file pointer to beginning if possible
    if hasattr(file, 'seek'):
        file.seek(0)

    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        if isinstance(chunk, str):
            chunk = chunk.encode('utf-8')
        digest.update(chunk)

    return digest.hexdigest()

def read_file_in_chunks(file_path, chunk_size=1024 * 1024 * 50):
    """
    Read a file in chunks for efficient memory usage during file processing.

    This function is particularly useful for large files or when you need to process
    files in chunks, such as for uploading or hashing.

    Args:
        file_path (str | Path): Path to the file to read
        chunk_size (int, optional): Size of each chunk in bytes. Defaults to 50MB (1024 * 1024 * 50)

    Yields:
        bytes: File content chunks

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read due to permissions
        OSError: If there's an OS-level error reading the file

    Example:
        ```python
        from synapse_sdk.utils.file import read_file_in_chunks

        # Read a file in 10MB chunks
        for chunk in read_file_in_chunks('large_file.bin', chunk_size=1024*1024*10):
            process_chunk(chunk)
        ```
    """
    with open(file_path, 'rb') as file:
        while chunk := file.read(chunk_size):
            yield chunk

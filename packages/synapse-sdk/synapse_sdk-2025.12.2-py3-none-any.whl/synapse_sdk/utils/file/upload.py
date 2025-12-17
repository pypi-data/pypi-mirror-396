"""File upload utilities for HTTP requests.

This module provides utilities for processing files for upload in HTTP requests,
with proper type definitions for file objects used in the requests library.
"""

from io import BufferedReader
from pathlib import Path
from typing import BinaryIO, TypeAlias, Union

# Type definitions for HTTP request file objects
# Based on requests library file parameter structure

# File tuple format: (filename, file_content)
# This is what we actually use when processing Path objects
FileTuple: TypeAlias = tuple[str, BinaryIO]

# Combined file type for requests library
# - bytes: Raw content (for chunked uploads)
# - FileTuple: (filename, file_handle) for Path objects
RequestsFile: TypeAlias = Union[bytes, FileTuple]

# Files dictionary mapping field names to file objects
FilesDict: TypeAlias = dict[str, RequestsFile]


class FileUploadError(Exception):
    """Base exception for file upload errors."""

    pass


class FileValidationError(FileUploadError):
    """Raised when file validation fails."""

    pass


class FileProcessingError(FileUploadError):
    """Raised when file processing fails."""

    pass


def process_files_for_upload(files: dict[str, Union[str, Path, bytes, object]]) -> tuple[FilesDict, list[BinaryIO]]:
    """Process files parameter for upload requests.

    Converts file paths to file handles suitable for requests library.
    Supports: str paths, Path objects, UPath objects (cloud storage), and bytes.

    This function standardizes file inputs into the proper structure for HTTP requests,
    handling various input types and ensuring proper resource management.

    Args:
        files: Dictionary mapping field names to file sources.
               Supported types:
               - str: File path (converted to Path)
               - pathlib.Path: Local file path
               - upath.UPath: Cloud storage path (GCS, S3, SFTP, etc.)
               - bytes: Raw file content (e.g., for chunked uploads)

               Example:
                   {'file': Path('/tmp/test.txt')}
                   {'document': 'uploads/doc.pdf'}
                   {'data': b'raw content'}

    Returns:
        tuple[FilesDict, list[BinaryIO]]: A tuple containing:
            - processed_files: Dictionary ready for requests library
              Maps field names to RequestsFile objects (tuples of filename + file handle)
            - opened_file_handles: List of opened file objects that need to be closed
              Caller is responsible for closing these handles after the request

    Raises:
        FileValidationError: If file value is None or has invalid type
        FileProcessingError: If file cannot be opened or read

    Example:
        >>> files = {'document': Path('/tmp/report.pdf'), 'metadata': b'{"version": 1}'}
        >>> processed, handles = process_files_for_upload(files)
        >>> try:
        ...     response = requests.post(url, files=processed)
        ... finally:
        ...     for handle in handles:
        ...         handle.close()

    Note:
        - String paths are automatically converted to pathlib.Path objects
        - Cloud storage paths (UPath) are supported via duck typing (has 'open' and 'name' attributes)
        - Bytes are passed through unchanged (useful for chunked uploads)
        - Opened file handles must be closed by the caller to prevent resource leaks
        - If file opening fails, any previously opened handles are automatically closed
    """
    processed_files: FilesDict = {}
    opened_file_handles: list[BinaryIO] = []

    for field_name, file_value in files.items():
        # 1. Validate: Reject None values with clear error message
        if file_value is None:
            raise FileValidationError(
                f"File field '{field_name}' cannot be None. "
                f'Provide a valid file path (str or Path), UPath object, or bytes.'
            )

        # 2. Handle bytes directly (for chunked uploads or raw content)
        if isinstance(file_value, bytes):
            processed_files[field_name] = file_value
            continue

        # 3. Convert string to Path for uniform handling
        if isinstance(file_value, str):
            file_value = Path(file_value)

        # 4. Handle Path-like objects (pathlib.Path and upath.UPath)
        #    Using duck typing to support both standard Path and cloud storage UPath
        if hasattr(file_value, 'open') and hasattr(file_value, 'name'):
            try:
                # Open file in binary read mode
                opened_file: BinaryIO = file_value.open(mode='rb')

                # Extract filename, use 'file' as fallback if name is empty
                filename = file_value.name if file_value.name else 'file'

                # Create file tuple: (filename, file_handle)
                processed_files[field_name] = (filename, opened_file)

                # Track opened handle for cleanup
                opened_file_handles.append(opened_file)

            except Exception as e:
                # Clean up already opened files before raising
                for f in opened_file_handles:
                    try:
                        f.close()
                    except Exception:
                        pass  # Ignore errors during cleanup

                raise FileProcessingError(f"Failed to open file '{file_value}' for field '{field_name}': {e}") from e

        else:
            # 5. Unsupported type - provide clear error message
            raise FileValidationError(
                f"File field '{field_name}' has unsupported type '{type(file_value).__name__}'. "
                f'Supported types: str (file path), pathlib.Path, upath.UPath, or bytes. '
                f'Got: {file_value!r}'
            )

    return processed_files, opened_file_handles


def close_file_handles(handles: list[BinaryIO]) -> None:
    """Safely close multiple file handles, ignoring errors.

    Args:
        handles: List of file handles to close

    Note:
        Errors during closing are silently ignored to ensure all handles
        are attempted to be closed even if some fail.
    """
    for handle in handles:
        try:
            handle.close()
        except Exception:
            pass  # Ignore errors during cleanup

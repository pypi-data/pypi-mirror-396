# File utilities module
# Maintains backward compatibility by re-exporting all functions

from .archive import archive, unarchive
from .checksum import calculate_checksum, get_checksum_from_file
from .chunking import read_file_in_chunks
from .download import (
    adownload_file,
    afiles_url_to_path,
    afiles_url_to_path_from_objs,
    download_file,
    files_url_to_path,
    files_url_to_path_from_objs,
)
from .encoding import convert_file_to_base64
from .io import get_dict_from_file, get_temp_path
from .upload import (
    FilesDict,
    FileProcessingError,
    FileTuple,
    FileUploadError,
    FileValidationError,
    RequestsFile,
    close_file_handles,
    process_files_for_upload,
)

__all__ = [
    # Chunking
    'read_file_in_chunks',
    # Download
    'download_file',
    'adownload_file',
    'files_url_to_path',
    'afiles_url_to_path',
    'files_url_to_path_from_objs',
    'afiles_url_to_path_from_objs',
    # Checksum
    'calculate_checksum',
    'get_checksum_from_file',
    # Archive
    'archive',
    'unarchive',
    # Encoding
    'convert_file_to_base64',
    # I/O
    'get_dict_from_file',
    'get_temp_path',
    # Upload
    'process_files_for_upload',
    'close_file_handles',
    'FileUploadError',
    'FileValidationError',
    'FileProcessingError',
    'FileTuple',
    'FilesDict',
    'RequestsFile',
]

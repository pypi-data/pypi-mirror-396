import base64
import mimetypes
from pathlib import Path


def convert_file_to_base64(file_path):
    """
    Convert a file to base64 using pathlib.

    Args:
        file_path (str): Path to the file to convert

    Returns:
        str: Base64 encoded string of the file contents
    """
    # FIXME base64 is sent sometimes.
    if file_path.startswith('data:'):
        return file_path

    # Convert string path to Path object
    path = Path(file_path)

    try:
        # Read binary content of the file
        binary_content = path.read_bytes()

        # Convert to base64
        base64_encoded = base64.b64encode(binary_content).decode('utf-8')

        # Get the MIME type of the file
        mime_type, _ = mimetypes.guess_type(path)
        assert mime_type is not None, 'MIME type cannot be guessed'

        # Convert bytes to string for readable output
        return f'data:{mime_type};base64,{base64_encoded}'

    except FileNotFoundError:
        raise FileNotFoundError(f'File not found: {file_path}')
    except Exception as e:
        raise Exception(f'Error converting file to base64: {str(e)}')

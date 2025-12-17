import zipfile
from pathlib import Path


def archive(input_path, output_path, append=False):
    input_path = Path(input_path)
    output_path = Path(output_path)

    mode = 'a' if append and output_path.exists() else 'w'
    with zipfile.ZipFile(output_path, mode=mode, compression=zipfile.ZIP_DEFLATED) as zipf:
        if input_path.is_file():
            zipf.write(input_path, input_path.name)
        else:
            for file_path in input_path.rglob('*'):
                if file_path.is_file():  # Only add files, skip directories
                    arcname = file_path.relative_to(input_path.parent)
                    zipf.write(file_path, arcname)


def unarchive(file_path, output_path):
    """
    Unarchives a ZIP file to a given directory.

    Parameters:
        file_path (str | Path): The path to the ZIP file.
        output_path (str): The directory where the files will be extracted.
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(str(file_path), 'r') as zip_ref:
        zip_ref.extractall(output_path)

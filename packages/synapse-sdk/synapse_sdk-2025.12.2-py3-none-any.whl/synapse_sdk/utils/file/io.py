import json
from pathlib import Path

import yaml


def get_dict_from_file(file_path):
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with open(file_path) as f:
        if file_path.suffix == '.yaml':
            return yaml.safe_load(f)
        else:
            return json.load(f)


def get_temp_path(sub_path=None):
    path = Path('/tmp/datamaker')
    if sub_path:
        path = path / sub_path
    return path

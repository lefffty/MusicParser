import os
import requests
import json
from pathlib import Path

from config import HEADERS
from utils import sanitize_filename


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_json(data, filepath: str) -> None:
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def download_image(url: str, filepath: str) -> bool:
    response = requests.get(url, stream=True, headers=HEADERS)
    if response.status_code == 200:
        ensure_dir(os.path.dirname(filepath))
        try:
            with open(filepath, 'wb') as f:
                f.write(response.content)
        except OSError:
            sanitized_filepath = Path(filepath)
            sanitized_filepath.rename(sanitize_filename(
                sanitized_filepath.name))
            with open(sanitized_filepath, 'wb') as f:
                f.write(response.content)
        return True
    return False

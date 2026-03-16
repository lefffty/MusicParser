import os
import requests
import json
from config import HEADERS


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
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return True
    return False

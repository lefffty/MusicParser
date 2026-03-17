from bs4 import BeautifulSoup
import requests
import time
from config import HEADERS


def fetch_soup(url: str, retries: int = 3, delay: int = 2) -> BeautifulSoup:
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (502, 503, 504) and attempt < retries - 1:
                sleep_time = delay * (2 ** attempt)
                print(
                    f"Получена ошибка {e.response.status_code}. Повтор через {sleep_time} сек...")
                time.sleep(sleep_time)
                continue
            raise
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                sleep_time = delay * (2 ** attempt)
                print(
                    f"Ошибка соединения: {e}. Повтор через {sleep_time} сек...")
                time.sleep(sleep_time)
                continue
            raise

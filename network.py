import requests
from bs4 import BeautifulSoup
from config import HEADERS


def fetch_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

from network import fetch_soup
from bs4 import BeautifulSoup


class BaseParser:
    def get_soup(self, url: str) -> BeautifulSoup:
        return fetch_soup(url)

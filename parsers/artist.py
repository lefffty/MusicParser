import requests
import re
from bs4 import BeautifulSoup

import urls
from config import SELECTORS, MAX_GENRES, GENRE_PATTERN, HEADERS
from parsers.base import BaseParser


class ArtistParser(BaseParser):
    def get_artists_by_genre_page(self, genre: str, page: int) -> list[str]:
        url = urls.genre_artists_url(genre, page)
        soup = self.get_soup(url)
        items = soup.find_all(
            SELECTORS['ARTISTS'][0],
            SELECTORS['ARTISTS'][1]
        )
        artists_on_page = [item.contents[0].text for item in items]
        return artists_on_page

    def get_artist_description(self, artist: str) -> str:
        url = urls.artist_description_url(artist)
        soup = self.get_soup(url)
        paragraphs = soup.find_all('p')
        texts = (paragraph.text for paragraph in paragraphs)
        return ' '.join(texts)

    def get_artist_image_url(self, artist: str) -> str:
        url = urls.artist_images_page_url(artist)
        soup = self.get_soup(url)
        item = soup.find_all(
            'a',
            'image-list-item'
        )[0]
        url = 'https://www.last.fm/' + item.attrs['href']
        soup = self.get_soup(url)
        item = soup.find_all(
            'img',
            'js-gallery-image',
        )
        image = item[0]
        return image.attrs['src']

    def get_similar_artists(self, artist: str):
        url = urls.similar_artists_url(artist)
        soup = self.get_soup(url)
        items = soup.find_all(
            'a',
            'link-block-target',
        )
        similar = [item.text for item in items]
        return similar

    def get_artist_genres(self, artist: str):
        url = urls.artist_tags_url(artist)
        soup = self.get_soup(url)
        items = soup.find_all(
            SELECTORS['ARTIST_GENRE_CLASS'][0],
            SELECTORS['ARTIST_GENRE_CLASS'][1]
        )
        genres = [item.text.strip()
                  for item in items if not re.search(GENRE_PATTERN, item.text.strip())]
        return genres[:MAX_GENRES]

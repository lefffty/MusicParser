import requests
import re
from bs4 import BeautifulSoup

import urls
from config import SELECTORS, MAX_GENRES, GENRE_PATTERN, HEADERS
from base import BaseParser


class ArtistsParser(BaseParser):
    def get_paginated_artists_by_genre(self, genre: str, page: int) -> list[str]:
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
        texts = [paragraph.text for paragraph in paragraphs]
        return ' '.join(texts)

    def get_artist_image_url(self, artist: str) -> str:
        url = urls.artist_description_url(artist)
        soup = self.get_soup(url)
        try:
            image_tag = soup.find_all(
                SELECTORS['GENUIS_ARTIST_IMAGE_CLASS'][0],
                SELECTORS['GENUIS_ARTIST_IMAGE_CLASS'][1]
            )[0]
            url = image_tag.contents[1]['style'].split(
                "url('")[1].split("')")[0]
            print(f'{artist} - {url}')
            return url
        except IndexError:
            img_url = urls.artist_images_page_url(artist)
            response = requests.get(img_url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            images_items = soup.find_all(
                SELECTORS['LAST_FM_ARTIST_IMAGE_CLASS'][0],
                SELECTORS['LAST_FM_ARTIST_IMAGE_CLASS'][1],
            )
            url = images_items[0].contents[1].attrs['src']
            print(f'{artist} - {url}')
            return url

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

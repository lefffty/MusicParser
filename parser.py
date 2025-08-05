from bs4 import BeautifulSoup
from collections import namedtuple
import os
import time
import requests


Artist = namedtuple('Artist', ['avatar', 'username', 'description'])
Album = namedtuple('Album', ['name', 'publication_date'])


GENRES_DIR = 'genres'
ARTIST_IMAGES = 'artist_images'


def ensure_directories_exists():
    """
    Функция, которая проверяет существование директорий
    """
    os.makedirs(GENRES_DIR, exist_ok=True)
    os.makedirs(ARTIST_IMAGES, exist_ok=True)


class MusicParser:
    def __init__(self):
        self.MAX_PAGES = ('li', 'pagination-page')
        self.PARAGRAPH = ('p')
        self.ARTISTS = ('h3', 'big-artist-list-title')
        self.PAGE_LIMIT = 3
        self.GENRES = [
            'rock', 'hip-hop', 'jazz',
            'british', 'punk', '80s',
        ]

    def __get_genre_artists_url(self, genre: str) -> str:
        """
        Функция, которая возвращает URL-адрес со списком исполнителей, поющих в данном жанре
        """
        return f'https://www.last.fm/ru/tag/{genre}/artists'

    def __get_artist_description_url(self, artist: str) -> str:
        """
        Функция, которая возвращает URL-адрес с описанием исполнителя
        """
        return f'https://genius.com/artists/{artist}'

    def __get_paginated_artists_url(self, genre: str, page: int) -> str:
        """
        Функция, которая возвращает URL-адрес со списком исполнителей по номеру страницы
        """
        return f'https://www.last.fm/ru/tag/{genre}/artists?page={page}'

    def __get_artist_images_url(self, artist: str):
        """
        Функция, которая возвращает URL-адрес со списком изображений исполнителя
        """
        return f'https://www.last.fm/ru/music/{artist}/+images'

    def get_max_pages(self, genre: str) -> int:
        """
        Функция, которая возвращает номер последней страницы исполнителей определенного жанра
        """
        url = self.__get_genre_artists_url(genre)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        all_list_items = soup.find_all(self.MAX_PAGES[0], self.MAX_PAGES[1])
        max_pages = [item.contents[1] for item in all_list_items][-1]
        return int(max_pages.text)

    def get_artist_description(self, artist: str):
        """
        Функция, которая возвращает описание исполнителя
        """
        url = self.__get_artist_description_url(artist)
        response = requests.get(url)
        if response.status_code != 200:
            return -1
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        texts = [paragraph.text for paragraph in paragraphs]
        return ' '.join(texts)

    def get_paginated_artists_by_genre(self, genre: str, page: int):
        """
        Функция, которая возвращает список исполнителей определенного жанра по
        номеру страницы
        """
        url = self.__get_paginated_artists_url(genre, page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all(self.ARTISTS[0], self.ARTISTS[1])
        artists_on_page = [item.contents[0].text for item in items]
        return artists_on_page

    def write_parsed_data(self):
        """
        Записать в файл собранные данные
        """
        max_genre_pages = [self.get_max_pages(genre) for genre in self.GENRES]

        for genre, max_pages in zip(self.GENRES, max_genre_pages):
            artists = []
            for page in range(1, min(self.PAGE_LIMIT, max_pages)):
                artists_on_page = self.get_paginated_artists_by_genre(
                    genre, page)

                for page_artist in artists_on_page:
                    self.get_artist_description(page_artist)

                artists.extend(artists_on_page)

            full_path = os.path.join(GENRES_DIR, f'{genre}_artists.txt')
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(artists))

    def load_parsed_artists_data(self):
        """
        Считать собранные данные из файла
        """
        all_artists = []
        image_urls = []
        for genre in self.GENRES:
            genre_artists = [line.strip() for line in open(
                f'genres/{genre}_artists.txt', 'r').readlines()]
            for artist in genre_artists:
                img_url = self.__get_artist_images_url(artist)
                response = requests.get(img_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                image_elements = soup.find_all('a', 'image-list-item')
                url = image_elements[0].contents[1].attrs['src']
            all_artists.append(genre_artists)
            image_urls.append(url)
        return all_artists, image_urls

    def download_and_save_artist_images(self):
        """
        Функция, которая сохраняет в папке изображения исполнителей
        """
        artists, urls = self.read_parsed_data()
        for artist, url in zip(artists, urls):
            save_path = os.path.join('genre_images', f'{artist}.png')
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)
            else:
                print('Error while parsing:', response.status_code)
            time.sleep(2)


def main():
    """
    Главная функция
    """
    # ensure_directories_exists()
    # parser = MusicParser()
    # description = parser.get_artist_description('Led Zeppelin')
    # print(description)


if __name__ == '__main__':
    main()

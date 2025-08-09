from bs4 import BeautifulSoup
from data_classes import Song
from datetime import time
from typing import Union
from dotenv import load_dotenv
import os
import json
import requests

from config import (
    SELECTORS,
    HEADERS,
)
from exceptions import (
    ArtistImageError,
)
from data_classes import (
    Artist,
    ArtistURL
)


load_dotenv()


GENRES_DIR = 'genres'
ARTIST_IMAGES = 'artist_images'


def ensure_directories_exists():
    """
    Функция, которая проверяет существование директорий
    """
    os.makedirs(GENRES_DIR, exist_ok=True)
    os.makedirs(ARTIST_IMAGES, exist_ok=True)


class MusicParser:
    def get_genre_artists_url(self, genre: str) -> str:
        """
        Возвращает URL-адрес со списком исполнителей, поющих в данном жанре

        Args:
            genre (str): название жанра

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/tag/{genre}/artists'

    def get_artist_description_url(self, artist: str) -> str:
        """
        Возвращает URL-адрес с описанием исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
        """
        return f'https://genius.com/artists/{artist}'

    def get_paginated_artists_url(self, genre: str, page: int) -> str:
        """
        Возвращает URL-адрес
        со списком исполнителей по номеру страницы

        Args:
            genre (str): название жанра
            page (str): номер страницы

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/tag/{genre}/artists?page={page}'

    def get_artist_images_url(self, artist: str):
        """
        Возвращает URL-адрес
        со списком изображений исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/music/{artist}/+images'

    def get_artist_albums_url(self, artist: str):
        """
        Возвращает URL-адрес со списком альбомов выбранного исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/music/{artist}/+albums?order=most_popular'

    def get_album_url(self, artist: str, album_title: str):
        """
        Возвращает URL-адрес альбома

        Args:
            artist (str): никнейм исполнителя
            album_title (str): название альбома

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/music/{artist}/{album_title}'

    def parse_duration_to_time(self, raw_duration: str) -> time:
        """
        Преобразует строку формата "%H:%M:%S" в объект time

        Args:
            raw_time (str): продолжительность песни, в формате "%H:%M:%S"

        Returns:
            time: продолжительность песни
        """
        parts = [int(part) for part in raw_duration.split(':')]
        num_of_parts = len(parts)
        match num_of_parts:
            case 1:
                _duration = time(0, 0, parts[0])
            case 2:
                _duration = time(0, *parts)
            case 3:
                _duration = time(*parts)
        return _duration

    def get_max_pages(self, genre: str) -> int:
        """
        Возвращает номер последней страницы исполнителей определенного жанра

        Args:
            genre (str): название жанра

        Returns:
            str: URL-адрес
        """
        url = self.get_genre_artists_url(genre)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        all_list_items = soup.find_all(
            SELECTORS['MAX_PAGES'][0],
            SELECTORS['MAX_PAGES'][1]
        )
        max_pages = [item.contents[1] for item in all_list_items][-1]
        return int(max_pages.text)

    def get_all_genres(self):
        url = 'https://www.last.fm/ru/music'
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all(
            SELECTORS['GENRE_CLASS'][0], SELECTORS['GENRE_CLASS'][1])
        genres = [item.text for item in items]
        return genres

    def get_artist_description(self, artist: str) -> str:
        """
        Возвращает описание исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
        """
        url = self.get_artist_description_url(artist)
        response = requests.get(url)
        if response.status_code != 200:
            return 'No description needed.'
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        texts = [paragraph.text for paragraph in paragraphs]
        return ' '.join(texts)

    def get_paginated_artists_by_genre(self, genre: str, page: int) -> list[str]:
        """
        Возвращает список исполнителей определенного жанра по
        номеру страницы

        Args:
            genre (str): название жанра
            page (int): номер страницы

        Returns:
            list[str]: список исполнителей
        """
        url = self.get_paginated_artists_url(genre, page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all(
            SELECTORS['ARTISTS'][0],
            SELECTORS['ARTISTS'][1]
        )
        artists_on_page = [item.contents[0].text for item in items]
        return artists_on_page

    def get_album_songs(self, artist: str, title: str) -> Union[list[Song], int]:
        """
        Возвращает список объектов Song альбома

        Args:
            artist (str): никнейм исполнителя
            title (str): название альбома

        Returns:
            list[Song]: список песен альбома
        """
        url = self.get_album_url(artist, title)
        response = requests.get(url)
        if response.status_code != 200:
            return -1
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_tracks = soup.find_all(
            SELECTORS['TRACK_CLASS'][0],
            SELECTORS['ARTISTS'][1]
        )
        raw_durations = soup.find_all(
            SELECTORS['TRACK_DURATION_CLASS'][0],
            SELECTORS['TRACK_DURATION_CLASS'][1]
        )
        tracks = [track.contents[1].text for track in raw_tracks]
        durations = [duration.text.strip() for duration in raw_durations]
        return [Song(name, self.parse_duration_to_time(duration))
                for name, duration in zip(tracks, durations)]

    def get_artist_albums(self, artist: str) -> Union[list[str], int]:
        """
        Возвращает список альбомов исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            list[str]: список названий альбомов
        """
        url = self.get_artist_albums_url(artist)
        response = requests.get(url)
        if response.status_code != 200:
            return -1
        soup = BeautifulSoup(response.text, 'html.parser')
        album_items = soup.find_all(
            SELECTORS['ALBUM_CLASS'][0],
            SELECTORS['ALBUM_CLASS'][1]
        )[4:]
        album_names = [item.contents[1].text for item in album_items]
        return album_names

    def get_current_genres(self):
        return [file for file in os.listdir('jsons/genre_artists')]

    def get_artist_image_url(self, artist: str):
        try:
            url = self.get_artist_description_url(artist)
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            image_tag = soup.find_all(
                SELECTORS['GENUIS_ARTIST_IMAGE_CLASS'][0],
                SELECTORS['GENUIS_ARTIST_IMAGE_CLASS'][1]
            )[0]
            url = image_tag.contents[1]['style'].split(
                "url('")[1].split("')")[0]
            print(f'{artist} - {url}')
        except IndexError:
            img_url = self.get_artist_images_url(artist)
            response = requests.get(img_url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            images_items = soup.find_all(
                SELECTORS['LAST_FM_ARTIST_IMAGE_CLASS'][0],
                SELECTORS['LAST_FM_ARTIST_IMAGE_CLASS'][1],
            )
            url = images_items[0].contents[1].attrs['src']
            print(f'{artist} - {url}')
        return url

    def is_page_parsed(self, genre_folder: str, target_file: str) -> bool:
        os.makedirs(genre_folder, exist_ok=True)
        current_files = os.listdir(genre_folder)
        return target_file in current_files

    def is_urls_parsed(self, urls_folder: str, target_file: str) -> bool:
        os.makedirs(urls_folder, exist_ok=True)
        current_files = os.listdir(urls_folder)
        return target_file in current_files

    def write_artists(self, artists, genre_path, genre):
        descriptions = []
        avatars = []
        for artist in artists:
            _avatar_path = f'{artist}.jpg'
            _description = self.get_artist_description(artist)
            print(f'{artist} - {_avatar_path}')
            descriptions.append(_description)
            avatars.append(_avatar_path)

        instances = [
            Artist(username, avatar, description).to_dict()
            for username, avatar, description in zip(
                artists, avatars, descriptions
            )
        ]

        with open(genre_path, 'w', encoding='utf-8') as file:
            json.dump(instances, file)
            print(f'"{genre}" artists was dumped into "{genre_path}"')

    def parse_artists(self, genre: str, page: int) -> None:
        if genre not in self.get_all_genres():
            return
        genre_max_pages = self.get_max_pages(genre)
        if page not in range(1, genre_max_pages):
            return

        target_file = f'page={page}.json'
        genre_folder = f'jsons/artists/{genre}'
        urls_folder = f'jsons/genre_artists/{genre}'
        urls_path = os.path.join(urls_folder, target_file)
        genre_path = os.path.join(genre_folder, target_file)

        if self.is_urls_parsed(urls_folder, target_file):
            print(
                f'Artist`s urls of genre {genre} from page {page} were already parsed!'
            )
        else:
            self.write_artists_urls(genre, page, urls_path)

        if self.is_page_parsed(genre_folder, target_file):
            print(
                f'Artists of genre "{genre}" from page {page} were already parsed!')
        else:
            artists = self.get_paginated_artists_by_genre(genre, page)
            self.write_artists(artists, genre_path, genre)
            self.save_images(genre, page)

    def save_images(self, genre: str, page: int):
        path = f'jsons/genre_artists/{genre}/page={page}.json'
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        for item in data:
            pic_name = f'{item["username"]}.jpg'
            avatars_folder = os.getenv('TARGET_AVATARS_FOLDER')
            path = os.path.join(avatars_folder, pic_name)
            response = requests.get(
                item['url'], stream=True, headers=HEADERS)
            if response.status_code == 200:
                with open(path, 'wb') as file:
                    file.write(response.content)
                print(f'Downloaded "{path}"')
            else:
                print('Error while parsing:', response.status_code)

    def write_artists_urls(self, genre: str, page: int, path: str) -> None:
        artists = self.get_paginated_artists_by_genre(genre, page)
        urls = []
        for artist in artists:
            url = self.get_artist_image_url(artist)
            urls.append(url)
        instances = [ArtistURL(artist, url).to_dict()
                     for artist, url in zip(artists, urls)]
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(instances, file)


def main():
    """
    Главная функция
    """
    parser = MusicParser()
    parser.parse_artists('reggae', 1)


if __name__ == '__main__':
    main()

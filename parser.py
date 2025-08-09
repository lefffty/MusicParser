from bs4 import BeautifulSoup
from datetime import time, date
from dotenv import load_dotenv
import os
import re
import json
import requests

from config import (
    SELECTORS,
    HEADERS,
)
from exceptions import (
    GenreError,
    PageNumberError,
)
from data_classes import (
    Artist,
    ArtistURL,
    AlbumURL,
    Album,
    Song
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

    def get_artist_albums_url(self, artist: str, page: int = 1):
        """
        Возвращает URL-адрес со списком альбомов выбранного исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/music/{artist}/+albums?order=most_popular&page={page}'

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

    def get_album_songs(self, artist: str, title: str) -> list[Song]:
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
        return [Song(name, self.parse_duration_to_time(duration)).to_dict()
                for name, duration in zip(tracks, durations)]

    def get_artist_albums(self, artist: str, page: int = 1) -> list[str]:
        """
        Возвращает список альбомов исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            list[str]: список названий альбомов
        """
        url = self.get_artist_albums_url(artist, page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        album_items = soup.find_all(
            SELECTORS['ALBUM_CLASS'][0],
            SELECTORS['ALBUM_CLASS'][1]
        )[4:]
        album_names = [item.contents[1].text for item in album_items]
        return album_names

    def get_artist_image_url(self, artist: str):
        """
        """
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
            raise GenreError

        genre_max_pages = self.get_max_pages(genre)

        if page not in range(1, genre_max_pages):
            raise PageNumberError

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

    def get_album_covers(self, artist: str, title: str) -> str:
        return f'https://www.last.fm/ru/music/{artist}/{title}/+images'

    def get_album_cover_url(self, artist: str, title: str):
        url = self.get_album_covers(artist, title)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        single_cover_url = 'https://www.last.fm' + \
            soup.find_all(
                SELECTORS['LAST_FM_ARTIST_IMAGE_CLASS'][0],
                SELECTORS['LAST_FM_ARTIST_IMAGE_CLASS'][1]
            )[0].attrs['href']
        response = requests.get(single_cover_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tag = soup.find(
            SELECTORS['IMG_TAG'][0],
            SELECTORS['IMG_TAG'][1]
        )
        return tag['src']

    def get_albums_max_pages(self, artist: str) -> int:
        url = self.get_artist_albums_url(artist, 1)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        item = soup.find_all(
            SELECTORS['MAX_PAGES'][0],
            SELECTORS['MAX_PAGES'][1],
        )[-1]
        return int(item.text.strip())

    def get_publication_date(self, artist: str, album_title: str):
        url = self.get_album_url(artist, album_title)
        response = requests.get(url)
        if response.status_code != 200:
            return -1
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_publication_date = soup.find_all(
            SELECTORS['ALBUM_PUBLICATION_DATE_CLASS'][0],
            SELECTORS['ALBUM_PUBLICATION_DATE_CLASS'][1]
        )
        if len(raw_publication_date) == 2:
            return date(2000, 1, 1)
        publication_date = self.parse_publication_date(
            raw_publication_date[1].text.strip())
        return publication_date

    def parse_publication_date(self, publication_date: str):
        months = {
            'января': 1, 'февраля': 2, 'марта': 3,
            'апреля': 4, 'мая': 5, 'июня': 6,
            'июля': 7, 'августа': 8, 'сентября': 9,
            'октября': 10, 'ноября': 11, 'декабря': 12,
            'январь': 1, 'февраль': 2, 'март': 3,
            'апрель': 4, 'май': 5, 'июнь': 6,
            'июль': 7, 'август': 8, 'сентябрь': 9,
            'октябрь': 10, 'ноябрь': 11, 'декабрь': 12,
        }
        parts = publication_date.split()
        match len(parts):
            case 1:
                return date(int(parts[0]), 1, 1)
            case 2:
                return date(int(parts[1]), months[parts[0].lower()], 1)
            case 3:
                return date(int(parts[2]), months[parts[1].lower()], int(parts[0]))

    def write_albums(self, artist: str, titles: list[str], albums_path: str):
        publication_dates = []
        covers = []
        for title in titles:
            publication_date = self.get_publication_date(artist, title)
            cover_path = f'{title}.jpg'
            publication_dates.append(publication_date)
            covers.append(cover_path)
            print(f'{title} - {publication_date} - {cover_path}')

        instances = [
            Album(title, publication_date, cover_path).to_dict()
            for title, publication_date, cover_path in zip(
                titles, publication_dates, covers
            )
        ]

        with open(albums_path, 'w', encoding='utf-8') as file:
            json.dump(instances, file)
            print(f'"{artist}" albums was dumped into "{albums_path}"')

    def sanitize_filename(self, filename) -> str:
        return re.sub(r'[\\/*?:"<>|]', '', filename)

    def parse_albums(self, artist: str, page: int = 1):
        filename = f'page={page}.json'
        urls_folder = f'jsons/albums_urls/{artist}'
        albums_folder = f'jsons/albums/{artist}'
        albums_path = os.path.join(albums_folder, filename)

        if self.is_urls_parsed(urls_folder, filename):
            print(
                f'"{artist}`s" albums covers urls from page {page} were already parsed!'
            )
        else:
            self.write_albums_urls(artist, page)

        if self.is_page_parsed(albums_folder, filename):
            print(
                f'"{artist}`s" albums from page {page} were already parsed!'
            )
        else:
            titles = self.get_artist_albums(artist, page)
            self.write_albums(artist, titles, albums_path)
            self.save_covers(artist, page)

    def save_covers(self, artist, page: int):
        path = f'jsons/albums_urls/{artist}/page={page}.json'
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        for item in data:
            title = self.sanitize_filename(item["title"])
            cover_name = f'{title}.jpg'
            albums_covers_folder = os.getenv('ALBUM_COVERS_FOLDER_PATH')
            path = os.path.join(albums_covers_folder, cover_name)
            response = requests.get(
                item["url"], stream=True, headers=HEADERS
            )
            if response.status_code == 200:
                with open(path, 'wb') as file:
                    file.write(response.content)
                print(f'Downloaded "{path}"')
            else:
                print('Error while parsing:', response.status_code)

    def write_albums_urls(self, artist: str, page: int = 1) -> None:
        titles = self.get_artist_albums(artist, page)
        instances = []
        for title in titles:
            url = self.get_album_cover_url(artist, title)
            print(f'{title} - {url}')
            instances.append(AlbumURL(title, url).to_dict())
        folder = f'jsons/albums_urls/{artist}'
        os.makedirs(folder, exist_ok=True)
        filename = f'page={page}.json'
        path = os.path.join(folder, filename)
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(instances, file)
        print(f'Albums of "{artist}" from page="{page}" was saved into {path}')


def main():
    """
    Главная функция
    """
    parser = MusicParser()
    parser.parse_albums('Dire Straits', 1)


if __name__ == '__main__':
    main()

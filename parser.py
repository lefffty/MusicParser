from bs4 import BeautifulSoup
from data_classes import Song
from datetime import time
import os
import json
import requests


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
        self.MAX_PAGES = (
            'li',
            'pagination-page'
        )
        self.PARAGRAPH = ('p')
        self.ARTISTS = (
            'h3',
            'big-artist-list-title'
        )
        self.ARTISTS_PAGE_LIMIT = 2
        self.ARTIST_ALBUMS_PAGE_LIMIT = 2
        self.GENRES = (
            'rock', 'hip-hop', 'jazz',
            'british', 'punk', '80s',
        )
        self.ALBUM_CLASS = (
            'h3',
            'resource-list--release-list-item-name'
        )
        self.TRACK_CLASS = (
            'td',
            'chartlist-name'
        )
        self.TRACK_DURATION_CLASS = (
            'td',
            'chartlist-duration'
        )
        self.artists = []
        self.songs = []
        self.albums = []
        self.genres = []

    def __get_genre_artists_url(self, genre: str) -> str:
        """
        Возвращает URL-адрес со списком исполнителей, поющих в данном жанре

        Args:
            genre (str): название жанра

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/tag/{genre}/artists'

    def __get_artist_description_url(self, artist: str) -> str:
        """
        Возвращает URL-адрес с описанием исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
        """
        return f'https://genius.com/artists/{artist}'

    def __get_paginated_artists_url(self, genre: str, page: int) -> str:
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

    def __get_artist_images_url(self, artist: str):
        """
        Возвращает URL-адрес
        со списком изображений исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/music/{artist}/+images'

    def __get_artist_albums_url(self, artist: str):
        """
        Возвращает URL-адрес со списком альбомов выбранного исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/music/{artist}/+albums?order=most_popular'

    def __get_album_url(self, artist: str, album_title: str):
        """
        Возвращает URL-адрес альбома

        Args:
            artist (str): никнейм исполнителя
            album_title (str): название альбома

        Returns:
            str: URL-адрес
        """
        return f'https://www.last.fm/ru/music/{artist}/{album_title}'

    def __parse_duration_to_time(self, raw_duration: str):
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
                return time(0, 0, parts[0])
            case 2:
                return time(0, *parts)
            case 3:
                return time(*parts)

    def get_max_pages(self, genre: str) -> int:
        """
        Возвращает номер последней страницы исполнителей определенного жанра

        Args:
            genre (str): название жанра

        Returns:
            str: URL-адрес
        """
        url = self.__get_genre_artists_url(genre)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        all_list_items = soup.find_all(self.MAX_PAGES[0], self.MAX_PAGES[1])
        max_pages = [item.contents[1] for item in all_list_items][-1]
        return int(max_pages.text)

    def get_artist_description(self, artist: str):
        """
        Возвращает описание исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            str: URL-адрес
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
        Возвращает список исполнителей определенного жанра по
        номеру страницы

        Args:
            genre (str): название жанра
            page (int): номер страницы

        Returns:
            list[str]: список исполнителей
        """
        url = self.__get_paginated_artists_url(genre, page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all(self.ARTISTS[0], self.ARTISTS[1])
        artists_on_page = [item.contents[0].text for item in items]
        return artists_on_page

    def get_artist_albums(self, artist: str):
        """
        Возвращает список альбомов исполнителя

        Args:
            artist (str): никнейм исполнителя

        Returns:
            list[str]: список названий альбомов
        """
        url = self.__get_artist_albums_url(artist)
        response = requests.get(url)
        if response.status_code != 200:
            return -1
        soup = BeautifulSoup(response.text, 'html.parser')
        album_items = soup.find_all(
            self.ALBUM_CLASS[0], self.ALBUM_CLASS[1])[4:]
        album_names = [item.contents[1].text for item in album_items]
        return album_names

    def get_album_songs(self, artist: str, title: str):
        """
        Возвращает список объектов Song альбома

        Args:
            artist (str): никнейм исполнителя
            title (str): название альбома

        Returns:
            list[Song]: список песен альбома
        """
        url = self.__get_album_url(artist, title)
        response = requests.get(url)
        if response.status_code != 200:
            return -1
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_tracks = soup.find_all(self.TRACK_CLASS[0], self.TRACK_CLASS[1])
        raw_durations = soup.find_all(
            self.TRACK_DURATION_CLASS[0], self.TRACK_DURATION_CLASS[1])
        tracks = [track.contents[1].text for track in raw_tracks]
        durations = [duration.text.strip() for duration in raw_durations]
        return [Song(name, self.__parse_duration_to_time(duration)) for name, duration in zip(tracks, durations)]

    def write_parsed_data(self):
        """
        Записывает в файл собранные данные

        Returns:
            None
        """
        max_genre_pages = [self.get_max_pages(genre) for genre in self.GENRES]

        for genre, max_pages in zip(self.GENRES, max_genre_pages):
            artists = []

            for page in range(1, min(self.ARTISTS_PAGE_LIMIT, max_pages)):
                artists_on_page = self.get_paginated_artists_by_genre(
                    genre, page)

                for artist in artists_on_page:
                    description = self.get_artist_description(artist)
                    albums = self.get_artist_albums(artist)

                    print(
                        f'{artist}\n\t\tdescription: {description[:20] if isinstance(description, str) else description}\n\t\talbums: {albums}')

                artists.extend(artists_on_page)

            full_path = os.path.join(GENRES_DIR, f'{genre}_artists.txt')
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(artists))
                print(
                    f'Записаны артисты в жанре {genre}, количество - {len(artists)}')

    def load_parsed_artists_data(self):
        """
        Читает и возвращает собранные данные из файла

        Returns:
            list[str]: список прочитанных исполнителей
            list[str]: список ссылок на изображение исполнителя
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

        Returns:
            None
        """
        artists, urls = self.load_parsed_artists_data()
        for artist, url in zip(artists, urls):
            save_path = os.path.join('genre_images', f'{artist}.png')
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(response.content)
            else:
                print('Error while parsing:', response.status_code)


def main():
    """
    Главная функция
    """
    parser = MusicParser()
    songs = parser.get_album_songs('Led Zeppelin', 'Led Zeppelin IV')
    with open('jsons/Led Zeppelin IV_songs.json', 'w') as file:
        json.dump([song.to_dict() for song in songs], file, indent=2)


if __name__ == '__main__':
    main()

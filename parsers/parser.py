import os
import re
import dotenv
import requests

from parsers.album import AlbumParser
from parsers.artist import ArtistParser
from parsers.genre import GenreParser
from storage import download_image
from db.manager import DatabaseManager
from db.config import DatabaseConfig
from data_classes import Artist, Album, Genre


dotenv.load_dotenv()


class MusicParserCoordinator:
    def __init__(self, db_config: DatabaseConfig):
        self.artist_parser = ArtistParser()
        self.album_parser = AlbumParser()
        self.genre_parser = GenreParser()
        self.db_config = db_config
        self.album_covers_folder: str | None = os.getenv('ALBUM_COVERS_FOLDER')
        self.artist_avatars_folder: str | None = os.getenv(
            'ARTIST_AVATARS_FOLDER')

    def parse_artist_data(self, artist: str):
        desc = self.artist_parser.get_artist_description(artist)
        img_url = self.artist_parser.get_artist_image_url(artist)
        img_path = os.path.join(
            self.artist_avatars_folder, f"{artist}.jpg")
        download_image(img_url, img_path)
        artist_dto = Artist(
            artist, f"artist_avatars/{artist}.jpg", desc).to_dict()
        return artist_dto

    def parse_artists_by_genre_page(self, genre: str, page: int):
        artists = self.artist_parser.get_artists_by_genre_page(genre, page)
        artist_ids: list[int] = []

        for artist in artists:
            artist_id = self.select_artist_id(artist)

            if artist_id is None:
                artist_dto = self.parse_artist_data(artist)
                artist_id = self.insert_artist(artist_dto)
            else:
                print('Skipping "artist" - "{}"'.format(artist))
                continue

            genres = self.genre_parser.get_artist_tags(artist)

            for genre in genres:
                name = genre.capitalize()

                if name == artist:
                    continue

                genre_id = self.select_genre_id(name)
                if genre_id is None:
                    genre_desc = self.genre_parser.get_genre_description(genre)
                    genre_dto = Genre(name, genre_desc).to_dict()
                    genre_id = self.insert_genre(genre_dto)
                else:
                    print('Skipping "genre" - "{}"'.format(name))
                    continue

                self.insert_artist_genre(artist_id, genre_id)

            artist_ids.append(artist_id)

        for artist, artist_id in zip(artists, artist_ids):
            self.parse_artist_albums(artist, artist_id)

    def parse_artist(self, artist: str):
        artist_id = self.select_artist_id(artist)

        if artist_id is None:
            artist_dto = self.parse_artist_data(artist)
            artist_id = self.insert_artist(artist_dto)

        similar_artists = self.artist_parser.get_similar_artists(artist)

        for similar_artist in similar_artists:
            similar_artist_id = self.select_artist_id(similar_artist)

            if similar_artist_id is None:
                try:
                    similar_artist_dto = self.parse_artist_data(similar_artist)
                    similar_artist_id = self.insert_artist(similar_artist_dto)
                except requests.exceptions.HTTPError:
                    print('Skipped "{}" due to HTTPError'.format(similar_artist))
                    continue

            self.insert_related_artist(artist_id, similar_artist_id)

        genres = self.genre_parser.get_artist_tags(artist)

        for genre in genres:
            name = genre.capitalize()

            if name == artist:
                continue

            genre_id = self.select_genre_id(name)
            if genre_id is None:
                genre_desc = self.genre_parser.get_genre_description(genre)
                genre_dto = Genre(name, genre_desc).to_dict()
                genre_id = self.insert_genre(genre_dto)
            else:
                print('Skipping "genre" - "{}"'.format(name))
                continue

            self.insert_artist_genre(artist_id, genre_id)

        self.parse_artist_albums(artist, artist_id)

    def parse_artist_albums(self, artist: str, artist_id: int, page: int = 1):
        albums = self.album_parser.get_artist_albums(artist, page)[6:]
        albums_data = []
        for album in albums:
            print(album)
            new_album = re.sub(r'[\\/*?:"<>|]', '', album)
            if new_album != album:
                print(album, new_album)
                continue

            album_id = self.select_album_id(album)

            if album_id is None:
                pub_date = self.album_parser.get_album_publication_date(
                    artist, new_album)
                temp = None
                while not temp:
                    temp = self.album_parser.get_album_cover_url(
                        artist, new_album)
                cover_url = temp[0]['src']
                cover_path = f"{new_album}.jpg"
                album_dto = Album(new_album, pub_date,
                                  f"album_covers/{album}.jpg").to_dict()
                album_id = self.insert_album(album_dto)
                download_image(cover_url, os.path.join(
                    self.album_covers_folder, cover_path))
            else:
                print('Skipping "album" - "{}"'.format(album))
                continue

            genres = self.genre_parser.get_album_tags(artist, album)

            for genre in genres:
                name = genre.capitalize()

                genre_id = self.select_genre_id(name)

                if genre_id is None:
                    try:
                        genre_desc = self.genre_parser.get_genre_description(
                            name)
                    except requests.exceptions.HTTPError:
                        genre_desc = ''
                    genre_dto = Genre(name, genre_desc).to_dict()
                    genre_id = self.insert_genre(genre_dto)

                self.insert_album_genre(album_id, genre_id)

            self.insert_artist_album(artist_id, album_id)
            albums_data.append(album_dto)
            songs = self.album_parser.get_album_songs(artist, new_album)
            song_ids = self.insert_songs(songs)
            self.insert_album_songs(album_id, song_ids)

    def select_album_id(self, name):
        with DatabaseManager(self.db_config) as db_manager:
            album_id = db_manager.get_object_id('album', (name,))
            return album_id

    def select_artist_id(self, name):
        with DatabaseManager(self.db_config) as db_manager:
            artist_id = db_manager.get_object_id('artist', (name,))
            return artist_id

    def select_genre_id(self, name):
        with DatabaseManager(self.db_config) as db_manager:
            genre_id = db_manager.get_object_id('genre', (name,))
            return genre_id

    def insert_related_artist(self, artist_id: int, similar_artist_id: int):
        params = {
            'artist_id': artist_id,
            'related_artist_id': similar_artist_id,
        }
        with DatabaseManager(self.db_config) as db_manager:
            db_manager.insert_object('related_artists', params)

    def insert_album_genre(self, album_id: int, genre_id: int):
        params = {
            'album_id': album_id,
            'genre_id': genre_id,
        }
        with DatabaseManager(self.db_config) as db_manager:
            db_manager.insert_object('album_genre', params)

    def insert_artist_genre(self, artist_id: int, genre_id: int):
        params = {
            'artist_id': artist_id,
            'genre_id': genre_id,
        }
        with DatabaseManager(self.db_config) as db_manager:
            db_manager.insert_object('artist_genre', params)

    def insert_genre(self, params: dict):
        with DatabaseManager(self.db_config) as db_manager:
            genre_id = db_manager.insert_object('genre', params, fetch=True)
            return genre_id

    def insert_album(self, params: dict):
        with DatabaseManager(self.db_config) as db_manager:
            album_id = db_manager.insert_object('album', params, fetch=True)
            return album_id

    def insert_artist(self, params: dict):
        with DatabaseManager(self.db_config) as db_manager:
            artist_id = db_manager.insert_object('artist', params, fetch=True)
            return artist_id

    def insert_album_songs(self, album_id: int, song_ids: list[int]):
        with DatabaseManager(self.db_config) as db_manager:
            for song_id in song_ids:
                params = {'album_id': album_id, 'song_id': song_id}
                db_manager.insert_object('album_song', params)

    def insert_artist_album(self, artist_id: int, album_id: int):
        params = {'album_id': album_id, 'artist_id': artist_id}
        with DatabaseManager(self.db_config) as db_manager:
            db_manager.insert_object(
                'album_artist', params)

    def insert_songs(self, songs: list[dict]) -> list[int]:
        song_ids = []

        with DatabaseManager(self.db_config) as db_manager:
            for song in songs:
                song_id = db_manager.insert_object('song', song, fetch=True)
                song_ids.append(song_id)

        return song_ids

    def update_artist_images(self, mismatched_artists: list[tuple[int, str]]):
        for artist_id, artist in mismatched_artists:
            img_url = self.artist_parser.get_artist_image_url(artist)
            img_path = os.path.join(
                self.artist_avatars_folder, f"{artist}.jpg")
            download_image(img_url, img_path)

            params = {
                'artist_id': artist_id,
                'avatar': f"artist_avatars/{artist}.jpg",
            }

            with DatabaseManager(self.db_config) as db_manager:
                db_manager.update_object('artist', params)

    def select_mismatched_artists(self):
        mismatched_artists = []

        with DatabaseManager(self.db_config) as db_manager:
            artists = db_manager.get_many('artist')

            for artist in artists:
                username = artist[1]
                avatar = artist[3]
                id = artist[0]
                slash_index = avatar.find('/')
                if username != avatar[slash_index + 1:-4] and id > 35:
                    mismatched_artists.append((id, username))

        return mismatched_artists

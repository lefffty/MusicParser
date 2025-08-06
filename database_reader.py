from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2 import (
    OperationalError,
)
import os


load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.user = os.getenv('DB_USER')
        self.name = os.getenv('DB_NAME')
        self.password = os.getenv('DB_PASSWORD')
        self.port = os.getenv('DB_PORT')
        self.host = os.getenv('DB_HOST')
        self.schema_name = os.getenv('SCHEMA_NAME')

    def __enter__(self):
        try:
            self.connection = connect(
                dbname=self.name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print('Подключение установлено!')
            return self
        except OperationalError as e:
            print(f'Ошибка подключения или неверный пароль/логин: {e}')
            raise

    def get_albums(self):
        albums_query = f'SELECT * FROM {self.schema_name}.albums_album;'
        with self.connection.cursor() as cursor:
            cursor.execute(albums_query)
            albums = cursor.fetchall()
        return albums

    def get_artists(self):
        artists_query = f'SELECT * FROM {self.schema_name}.artist_artist;'
        with self.connection.cursor() as cursor:
            cursor.execute(artists_query)
            artists = cursor.fetchall()
        return artists

    def get_genres(self):
        genres_query = f'SELECT * FROM {self.schema_name}.genre_genre;'
        with self.connection.cursor() as cursor:
            cursor.execute(genres_query)
            genres = cursor.fetchall()
        return genres

    def get_songs(self):
        songs_query = f'SELECT * FROM {self.schema_name}.song_song;'
        with self.connection.cursor() as cursor:
            cursor.execute(songs_query)
            songs = cursor.fetchall()
        return songs

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        print('Подключение разорвано!')


print('Входим в контекстный менеджер!')
with DatabaseManager() as dr:
    artists = dr.get_artists()
    artist_names = [username for _, username, *_ in artists]
    print(artist_names)
print('Вышли из контекстного менеджера!')

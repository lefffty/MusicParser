from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2 import (
    OperationalError,
)
import json
import time
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

    def insert_artist(self, username: str, description: str, avatar: str):
        media_folder = os.getenv('RELATIVE_MEDIA_FOLDER')
        avatar = os.path.join(media_folder, avatar)
        if description != 'No description needed.':
            description = description[:description.find('.') + 1]
        artist_query = '''
            INSERT INTO public.artist_artist(username, description, avatar)
	        VALUES (%s, %s, %s);
        '''
        with self.connection.cursor() as cursor:
            cursor.execute(
                artist_query, (username, description, avatar))
            self.connection.commit()
        print(
            f'"Artist" with params ({username},{description},{avatar})')
        time.sleep(0.75)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        print('Подключение разорвано!')


def main():
    genre = '80s'
    print('Входим в контекстный менеджер!')
    with DatabaseManager() as dr:
        with open(f'jsons/artists/{genre}.json', 'r', encoding='utf-8') as file:
            data: list[dict] = json.load(file)
        for item in data:
            dr.insert_artist(*item.values())
    print('Вышли из контекстного менеджера!')


if __name__ == '__main__':
    main()

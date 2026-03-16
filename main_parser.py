import os
from parsers.album import AlbumParser
from parsers.artist import ArtistParser
from parsers.genre import GenreParser
from storage import download_image, write_json
from data_classes import Artist, Album
from config import GENRES_DIR, ARTIST_IMAGES


class MusicParserCoordinator:
    def __init__(self):
        self.artist_parser = ArtistParser()
        self.album_parser = AlbumParser()
        self.genre_parser = GenreParser()

    def parse_artists_by_genre_page(self, genre: str, page: int):
        """Полный цикл обработки страницы исполнителей жанра."""
        artists = self.artist_parser.get_artists_by_genre_page(genre, page)

        artists_data = []
        for artist in artists:
            desc = self.artist_parser.get_artist_description(artist)
            img_url = self.artist_parser.get_artist_image_url(artist)
            img_path = os.path.join(ARTIST_IMAGES, f"{artist}.jpg")
            download_image(img_url, img_path)
            artists_data.append(
                Artist(artist, f"{artist}.jpg", desc).to_dict())

        json_path = os.path.join(GENRES_DIR, genre, f"page={page}.json")
        write_json(artists_data, json_path)

        for artist in artists:
            self.parse_artist_albums(artist)

    def parse_artist_albums(self, artist: str, page: int = 1):
        """Парсинг альбомов исполнителя на указанной странице."""
        albums = self.album_parser.get_artist_albums(artist, page)
        albums_data = []
        for album in albums:
            pub_date = self.album_parser.get_album_publication_date(
                artist, album)
            cover_url = self.album_parser.get_album_cover_url(artist, album)
            cover_path = f"{album}.jpg"
            albums_data.append(Album(album, pub_date, cover_path).to_dict())
            download_image(cover_url, os.path.join("covers", cover_path))
            songs = self.album_parser.get_album_songs(artist, album)
            write_json(songs, os.path.join("songs", artist, f"{album}.json"))

        write_json(albums_data, os.path.join(
            "albums", artist, f"page={page}.json"))

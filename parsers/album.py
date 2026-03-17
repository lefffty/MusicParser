import re
from datetime import date

import urls
from data_classes import Song
from parsers.base import BaseParser
from config import SELECTORS, MAX_GENRES, GENRE_PATTERN
from utils import parse_duration_to_time, parse_publication_date


class AlbumParser(BaseParser):
    def get_artist_albums(self, artist: str, page: int = 1) -> list[str]:
        url = urls.artist_albums_url(artist, page)
        soup = self.get_soup(url)
        album_items = soup.find_all(
            SELECTORS['ALBUM_CLASS'][0],
            SELECTORS['ALBUM_CLASS'][1]
        )
        album_names = [item.contents[1].text for item in album_items]
        return album_names

    def get_album_cover_url(self, artist: str, album: str) -> list[dict]:
        url = urls.album_page_url(artist, album)
        soup = self.get_soup(url)
        items = soup.find_all(
            SELECTORS['LAST_FM_ARTIST_IMAGE_CLASS'][0],
            SELECTORS['LAST_FM_ARTIST_IMAGE_CLASS'][1]
        )
        img_tag = 'https://www.last.fm' + items[0].attrs['href']
        soup = self.get_soup(img_tag)
        full_imgs = soup.find_all(
            SELECTORS['IMG_TAG'][0],
            SELECTORS['IMG_TAG'][1]
        )
        return full_imgs

    def get_album_publication_date(self, artist: str, album: str) -> date:
        url = urls.album_page_url(artist, album)
        soup = self.get_soup(url)
        raw_publication_date = soup.find_all(
            SELECTORS['ALBUM_PUBLICATION_DATE_CLASS'][0],
            SELECTORS['ALBUM_PUBLICATION_DATE_CLASS'][1]
        )
        if len(raw_publication_date) == 2:
            return date(2000, 1, 1)
        try:
            publication_date = parse_publication_date(
                raw_publication_date[1].text.strip())
        except IndexError:
            publication_date = None
        return publication_date

    def get_album_songs(self, artist: str, album: str) -> list[dict]:
        url = urls.album_page_url(artist, album)
        soup = self.get_soup(url)
        raw_tracks = soup.find_all(
            SELECTORS['TRACK_CLASS'][0],
            SELECTORS['TRACK_CLASS'][1]
        )
        raw_durations = soup.find_all(
            SELECTORS['TRACK_DURATION_CLASS'][0],
            SELECTORS['TRACK_DURATION_CLASS'][1]
        )
        tracks = [track.contents[1].text for track in raw_tracks]
        durations = [duration.text.strip() for duration in raw_durations]
        return [Song(name, parse_duration_to_time(duration)).to_dict()
                for name, duration in zip(tracks, durations)]

    def get_album_genres(self, artist: str, album: str):
        url = urls.album_tags_url(artist, album)
        soup = self.get_soup(url)
        items = soup.find_all(
            SELECTORS['ALBUM_GENRE_CLASS'][0],
            SELECTORS['ALBUM_GENRE_CLASS'][1]
        )
        genres = [item.text.strip()
                  for item in items if not re.search(GENRE_PATTERN, item.text.strip())]
        return genres[:MAX_GENRES]

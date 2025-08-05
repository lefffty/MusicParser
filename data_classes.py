from typing import NamedTuple
import datetime


DATE_FORMAT = '%Y-%m-%d'


class Artist(NamedTuple):
    """
    Класс сущности <<Исполнитель>>
    """
    username: str
    avatar: str
    description: str

    def to_dict(self):
        return {
            'username': self.username,
            'description': self.description,
            'avatar': self.avatar
        }


class Album(NamedTuple):
    """
    Класс сущности <<Альбом>>
    """
    name: str
    publication_date: datetime.date

    def to_dict(self):
        return {
            'name': self.name,
            'publication_date': self.publication_date
        }


class Song(NamedTuple):
    """
    Класс сущности <<Песня>>
    """
    name: str
    duration: datetime.time

    def to_dict(self):
        return {
            'name': self.name,
            'duration': self.duration
        }


class Genre(NamedTuple):
    """
    Класс сущности <<Жанр>>
    """
    name: str
    description: str

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description
        }

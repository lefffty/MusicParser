from typing import NamedTuple
import datetime


class Artist(NamedTuple):
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
    name: str
    publication_date: datetime.date

    def to_dict(self):
        return {
            'name': self.name,
            'publication_date': self.publication_date
        }


class Song(NamedTuple):
    name: str
    duration: datetime.time

    def to_dict(self):
        return {
            'name': self.name,
            'duration': self.duration
        }


class Genre(NamedTuple):
    name: str
    description: str

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description
        }

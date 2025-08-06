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
    cover_path: str

    def to_dict(self):
        return {
            'name': self.name,
            'publication_date': self.publication_date.isoformat(),
            'cover': self.cover_path
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
            'duration': self.duration.isoformat()
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


if __name__ == '__main__':
    song = Song(
        name='blabla',
        duration=datetime.time(0, 1, 1)
    )
    print(song)

from urllib.parse import quote


def quoted(func):
    def wrapper(*args):
        args_list = []
        for arg in args:
            if not isinstance(arg, int):
                args_list.append(quote(arg))
            else:
                args_list.append(arg)
        return func(*args_list)
    return wrapper


@quoted
def genre_artists_url(genre: str, page: int) -> str:
    return f'https://www.last.fm/ru/tag/{genre}/artists?page={page}'


@quoted
def artist_page_url(artist: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}'


@quoted
def artist_description_url(artist: str) -> str:
    return f'https://genius.com/artists/{artist}'


@quoted
def artist_images_page_url(artist: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}/+images'


@quoted
def artist_albums_url(artist: str, page: int) -> str:
    return f'https://www.last.fm/ru/music/{artist}/+albums?order=most_popular&page={page}'


@quoted
def album_page_url(artist: str, album: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}/{album}'


@quoted
def album_tags_url(artist: str, album: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}/{album}/+tags'


@quoted
def artist_tags_url(artist: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}/+tags'


@quoted
def genre_wiki_url(genre: str) -> str:
    return f'https://www.last.fm/ru/tag/{genre}/wiki'


@quoted
def all_genres_url() -> str:
    return 'https://www.last.fm/ru/music'


@quoted
def similar_artists_url(artist: str):
    return f'https://www.last.fm/ru/music/{artist}/+similar'

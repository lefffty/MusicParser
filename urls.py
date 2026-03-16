def genre_artists_url(genre: str, page: int = 1) -> str:
    return f'https://www.last.fm/ru/tag/{genre}/artists?page={page}'


def artist_description_url(artist: str) -> str:
    return f'https://genius.com/artists/{artist}'


def artist_images_page_url(artist: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}/+images'


def artist_albums_url(artist: str, page: int = 1) -> str:
    return f'https://www.last.fm/ru/music/{artist}/+albums?order=most_popular&page={page}'


def album_page_url(artist: str, album: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}/{album}'


def album_tags_url(artist: str, album: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}/{album}/+tags'


def artist_tags_url(artist: str) -> str:
    return f'https://www.last.fm/ru/music/{artist}/+tags'


def genre_wiki_url(genre: str) -> str:
    return f'https://www.last.fm/ru/tag/{genre}/wiki'


def all_genres_url() -> str:
    return 'https://www.last.fm/ru/music'


# def get_album_url(artist: str, title: str, page: int = 1) -> str:
#     url = get_artist_albums_url(artist, 1)
#     response = requests.get(url, HEADERS)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     tags = [tag.contents[1] for tag in soup.find_all(
#         'h3', 'resource-list--release-list-item-name')]
#     urls = {tag.text: tag.attrs['href'] for tag in tags}
#     return 'https://www.last.fm' + urls[title]

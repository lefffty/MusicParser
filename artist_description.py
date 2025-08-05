from bs4 import BeautifulSoup
import requests


def __get_artist_description_url(artist: str) -> str:
    return f'https://genius.com/artists/{artist}'


def get_descriptions():
    # artists = [line.strip() for line in open(
    #     'genres/hip-hop_artists.txt', 'r').readlines()]
    # result = []
    # for artist in artists:
    url = __get_artist_description_url('21 Savage')
    response = requests.get(url)
    if response.status_code != 200:
        return -1
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    texts = [paragraph.text for paragraph in paragraphs]
    return ' '.join(texts)


print(get_descriptions())

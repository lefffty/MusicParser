from bs4 import BeautifulSoup
import requests
import os
import time


def ensure_directory_exists():
    os.makedirs('genre_images', exist_ok=True)


def get_artist_images_url(artist: str):
    return f'https://www.last.fm/ru/music/{artist}/+images'


def read_genre_artists():
    artists = [line.strip() for line in open(
        'genres/hip-hop_artists.txt', 'r').readlines()]
    urls = []
    for artist in artists:
        img_url = get_artist_images(artist)
        response = requests.get(img_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        images_items = soup.find_all('a', 'image-list-item')
        url = images_items[0].contents[1].attrs['src']
        urls.append(url)
    return artists, urls


def get_images():
    artists, urls = read_genre_artists()
    for artist, url in zip(artists, urls):
        save_path = os.path.join('genre_images', f'{artist}.png')
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
        else:
            print('Error while parsing:', response.status_code)
        time.sleep(2)


def main():
    ensure_directory_exists()
    get_images()


if __name__ == '__main__':
    main()

import sys
import keyboard

from parsers.genre import GenreParser
from parsers.artist import ArtistParser
from db.config import DatabaseConfig
from parsers.parser import MusicParserCoordinator


db_config = DatabaseConfig('config.yaml')
parser = MusicParserCoordinator(db_config)


def flush_stdin():
    """Очищает буфер ввода stdin."""
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except ImportError:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


def display_genres(genres: list[str], num_of_spaces: int):
    for index, genre in enumerate(genres):
        print('{}{} - {}'.format(num_of_spaces * ' ', index + 1, genre))


def clear_last_lines(n: int):
    for _ in range(n):
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')
    sys.stdout.flush()


def display_artists(artists: list[str], num_of_spaces: int):
    for index, artist in enumerate(artists):
        print('{}{} - {}'.format(num_of_spaces * ' ', index + 1, artist))


def get_chosen_genre_page(min_page: int, max_page: int, genre: str):
    page = min_page
    while True:

        artists = get_artists(genre, page)
        print(
            f"Страница {page} из {max_page}. Используйте стрелки для навигации, 'q' для выхода.")
        display_artists(artists, 3)

        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            clear_last_lines(len(artists) + 1)
            if event.name == 'left':
                if page > min_page:
                    page -= 1
            elif event.name == 'right':
                if page < max_page:
                    page += 1
            elif event.name == 'enter':
                flush_stdin()
                index = int(input('Enter index: ')) - 1
                artist = artists[index]
                parser.parse_artist(artist)
            elif event.name == 'q':
                return None


def get_artists(genre: str, page: int):
    artist_parser = ArtistParser()
    artists = artist_parser.get_artists_by_genre_page(genre, page)
    return artists


def display_genre_interface(genre_parser: GenreParser, genre: str):
    min_page = 1
    max_page = genre_parser.get_max_pages_for_genre(genre)
    chosen_page = get_chosen_genre_page(min_page, max_page, genre)

    return chosen_page


def main():
    genre_parser = GenreParser()
    artist_parser = ArtistParser()

    genres = genre_parser.get_all_genres() + ['pop']

    print('1 - choose genre')
    print('2 - exit')

    choice = int(input('Enter your choice: '))

    match choice:
        case 1:
            clear_last_lines(1)
            while True:
                display_genres(genres, 2)
                index = int(input('Enter genre index: ')) - 1
                clear_last_lines(1)
                genre = genres[index]
                page = display_genre_interface(genre_parser, genre)
        case 2:
            clear_last_lines(1)
            sys.exit(0)


if __name__ == '__main__':
    main()

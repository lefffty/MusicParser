from parsers.base import BaseParser
import urls
from config import SELECTORS


class GenreParser(BaseParser):
    def get_all_genres(self) -> list[str]:
        """Возвращает список всех жанров с главной страницы музыки."""
        url = urls.all_genres_url()
        soup = self.get_soup(url)
        items = soup.find_all(SELECTORS['GENRE_CLASS'][0],
                              SELECTORS['GENRE_CLASS'][1])
        return [item.text for item in items]

    def get_genre_description(self, genre: str) -> str:
        """Возвращает краткое описание жанра (первые три предложения)."""
        url = urls.genre_wiki_url(genre)
        soup = self.get_soup(url)
        raw = soup.find_all(SELECTORS['GENRE_DESCRIPTION_CLASS'][0],
                            SELECTORS['GENRE_DESCRIPTION_CLASS'][1])
        if not raw:
            return ""
        full_text = raw[0].text.strip()
        sentences = full_text.split('.')[:3]
        return '. '.join(sentences) + '.'

    def get_max_pages_for_genre(self, genre: str) -> int:
        """Возвращает максимальный номер страницы для списка исполнителей жанра."""
        url = urls.genre_artists_url(genre, page=1)
        soup = self.get_soup(url)
        pagination_items = soup.find_all(SELECTORS['MAX_PAGES'][0],
                                         SELECTORS['MAX_PAGES'][1])
        last_page = pagination_items[-1].contents[1].text
        return int(last_page)

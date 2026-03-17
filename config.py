SELECTORS = {
    'MAX_PAGES': (
        'li',
        'pagination-page'
    ),
    'PARAGRAPH': (
        'p',
    ),
    'ARTISTS': (
        'h3',
        'big-artist-list-title'
    ),
    'ALBUM_CLASS': (
        'h3',
        'resource-list--release-list-item-name'
    ),
    'TRACK_CLASS': (
        'td',
        'chartlist-name'
    ),
    'TRACK_DURATION_CLASS': (
        'td',
        'chartlist-duration'
    ),
    'GENRE_CLASS': (
        'span',
        'music-more-tags-tag-link',
    ),
    'GENUIS_ARTIST_IMAGE_CLASS': (
        'div',
        'column_layout-column_span column_layout-column_span--secondary'
    ),
    'LAST_FM_ARTIST_IMAGE_CLASS': (
        'a',
        'js-link-block-cover-link link-block-cover-link',
    ),
    'IMG_TAG': (
        'img',
        'js-gallery-image'
    ),
    'ALBUM_PUBLICATION_DATE_CLASS': (
        'dd',
        'catalogue-metadata-description'
    ),
    'ALBUM_GENRE_CLASS': (
        'h3',
        'big-tags-item-name',
    ),
    'GENRE_DESCRIPTION_CLASS': (
        'div',
        'wiki-content'
    ),
    'ARTIST_GENRE_CLASS': (
        'h3',
        'big-tags-item-name'
    )
}

LIMITS = {
    'ARTISTS_PAGE_LIMIT': 2,
    'ARTIST_ALBUMS_PAGE_LIMIT': 2,
}

ENUMS = {
    'GENRES': (
        'rock', 'hip-hop', 'jazz',
        'british', 'punk', '80s',
    ),
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.google.com/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1'
}


GENRES_DIR = 'genres'
ARTIST_IMAGES = 'artist_images'
GENRE_PATTERN = r'\d'
MAX_GENRES = 5
COMMON_FOLDER = 'jsons'

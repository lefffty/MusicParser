import re
from datetime import time, date


def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', '', filename)


def parse_duration_to_time(raw_duration: str) -> time:
    if not raw_duration:
        return time(0, 0, 0)
    parts = [int(part) for part in raw_duration.split(':')]
    num_of_parts = len(parts)
    match num_of_parts:
        case 1:
            _duration = time(0, 0, parts[0])
        case 2:
            _duration = time(0, *parts)
        case 3:
            _duration = time(*parts)
    return _duration


def parse_publication_date(publication_date: str):
    months = {
        'января': 1, 'февраля': 2, 'марта': 3,
        'апреля': 4, 'мая': 5, 'июня': 6,
        'июля': 7, 'августа': 8, 'сентября': 9,
        'октября': 10, 'ноября': 11, 'декабря': 12,
        'январь': 1, 'февраль': 2, 'март': 3,
        'апрель': 4, 'май': 5, 'июнь': 6,
        'июль': 7, 'август': 8, 'сентябрь': 9,
        'октябрь': 10, 'ноябрь': 11, 'декабрь': 12,
    }
    parts = publication_date.split()
    match len(parts):
        case 1:
            return date(int(parts[0]), 1, 1)
        case 2:
            return date(int(parts[1]), months[parts[0].lower()], 1)
        case 3:
            return date(int(parts[2]), months[parts[1].lower()], int(parts[0]))

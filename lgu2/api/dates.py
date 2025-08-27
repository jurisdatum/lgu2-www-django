
from datetime import date

from . import server


class DateCount:
    date: date
    count: int


def get_recently_published_dates():
    url = '/dates/published'
    date_counts = server.get_json(url)
    for count in date_counts:
        count['date'] = date.fromisoformat(count['date'])
    return date_counts

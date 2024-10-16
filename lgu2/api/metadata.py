
from . import server


def get_metadata(type: str, year, number):
    url = '/metadata/' + type + '/' + str(year) + '/' + str(number)
    return server.get_json(url)

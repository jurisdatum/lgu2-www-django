
from . import server


def get_metadata(type: str, year, number):
    url = '/metadata/' + type + '/' + str(year) + '/' + str(number)
    return server.get_json(url)


def get_metadata_list(type: str, year):
    url = '/metadata/' + type + '/' + str(year)
    return server.get_json(url)
from . import server

def check_health():
    url = '/health'
    response = server.get_json(url, None)
    return response
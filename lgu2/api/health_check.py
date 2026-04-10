from . import server

def check_health():
    url = '/health'
    response = server.get(url, 'application/json')
    return response

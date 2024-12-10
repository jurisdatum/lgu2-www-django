
def use_new_theme(request):
    # if request.GET.get('theme', None) == 'old':
    #     return False
    if request.GET.get('theme', None) == 'new':
        return True
    # if 'theme' in request.COOKIES and request.COOKIES['theme'] == 'new':
    #     return True
    return False


def set_new_theme(response):
    response.set_cookie('theme', 'new', max_age=2592000)


def remove_new_theme(response):
    response.delete_cookie('theme')

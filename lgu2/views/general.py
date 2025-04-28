from django.http import HttpResponse
from django.template import loader


def homepage(request):
    print('tigger')
    template = loader.get_template('new_theme/index.html')
    return HttpResponse(template.render())

from django.shortcuts import render

from ..api import documents as api
from lgu2.util.labels import get_type_label


def homepage(request):
    data = api.get_new()
    for doc in data['documents'][:5]:
        doc['typeLabel'] = get_type_label(doc['longType'])
    context = {
        'new_legislation': data['documents'][:5]
    }
    return render(request, 'new_theme/index.html', context)

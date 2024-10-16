
from django.http import HttpResponse
from django.template import loader

from ..api.doc_types import get_uk_types, Response
from ..util.labels import get_long_type_label


def list_uk(request):
    data: Response = get_uk_types()
    for type in data['primarily']:
        type['label'] = get_long_type_label(type['shortName'])
    for type in data['possibly']:
        type['label'] = get_long_type_label(type['shortName'])
    template = loader.get_template('browse/browse_uk.html')
    return HttpResponse(template.render(data, request))

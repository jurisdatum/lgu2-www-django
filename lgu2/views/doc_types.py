
from django.http import HttpResponse
from django.template import loader

from ..api.doc_types import get_types, Response
from ..util.labels import get_long_type_label

from ..models import Footer
def list_types(request, country):
    
    data: Response = get_types(country)

    for type in data['primarily']:
        type['label'] = get_long_type_label(type['shortName'])
    for type in data['possibly']:
        type['label'] = get_long_type_label(type['shortName'])

    data['country_heading'] = {
        'uk': 'UK',
        'wales': 'Wales',
        'scotland': 'Scotland',
        'ni': 'Northern Ireland',
    }[country]
    data['country_name'] = {
        'uk': 'the UK',
        'wales': 'Wales',
        'scotland': 'Scotland',
        'ni': 'Northern Ireland',
    }[country]

    data['footer'] = Footer.objects.all().first()

    template = loader.get_template('browse/browse_uk.html')
    return HttpResponse(template.render(data, request))

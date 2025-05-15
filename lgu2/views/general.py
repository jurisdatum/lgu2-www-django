
import json
import os

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from ..api import documents as api
from ..api.doc_types import get_types, Response
from lgu2.util.labels import get_singular_type_label, get_long_type_label

@cache_page(60 * 15)
def homepage(request):
    data = api.get_new()
    for doc in data['documents'][:5]:
        doc['typeLabel'] = get_singular_type_label(doc['longType'])
        if doc['version'] == 'enacted':
            doc['link'] = '/' + doc['id'] + '/contents/' + doc['version']
        elif doc['version'] == 'made':
            doc['link'] = '/' + doc['id'] + '/contents/' + doc['version']
        else:
            doc['link'] = '/' + doc['id'] + '/contents'

    context = {
        'new_legislation': data['documents'][:5]
    }
    return render(request, 'new_theme/index.html', context)


def explore_collection(request):
    return render(request, 'new_theme/explore_collection/explore_our_collection.html')


def different_legislature(request):
    return render(request, 'new_theme/explore_collection/different_legislatures.html')


def different_legislature_by_country(request, country):
    
    data: Response = get_types(country)

    for type in data['primarily']:
        type['label'] = get_long_type_label(type['shortName'])
    for type in data['possibly']:
        type['label'] = get_long_type_label(type['shortName'])

    result = {
        'apply_primary': [],
        'apply_secondary': [],
        'may_primary': [],
        'may_secondary': []
    }

    # Process 'primarily'
    for item in data['primarily']:
        if item['category'] == 'primary':
            item['label'] = get_long_type_label(item['shortName'])
            result['apply_primary'].append(item)
        elif item['category'] == 'secondary':
            item['label'] = get_long_type_label(item['shortName'])
            result['apply_secondary'].append(item)

    # Process 'possibly'
    for item in data.get('possibly', []):
        if item['category'] == 'primary':
            item['label'] = get_long_type_label(item['shortName'])
            result['may_primary'].append(item)
        elif item['category'] == 'secondary':
            item['label'] = get_long_type_label(item['shortName'])
            result['may_secondary'].append(item)

    result['country_heading'] = {
        'uk': 'the United Kingdom',
        'wales': 'Wales',
        'scotland': 'Scotland',
        'ni': 'Northern Ireland',
    }[country]
    result['country_name'] = {
        'uk': 'the UK',
        'wales': 'Wales',
        'scotland': 'Scotland',
        'ni': 'Northern Ireland',
    }[country]

    json_path = os.path.join(settings.BASE_DIR, 'lgu2', 'views', 'country_texts.json')

    with open(json_path, 'r', encoding='utf-8') as file:
        country_texts = json.load(file)

    result["country_text"] = country_texts[country]
    return render(request, 'new_theme/explore_collection/different_country_legislature.html', result)


def legislature_eu_exit_uk_law(request):
    return render(request, 'new_theme/explore_collection/explore-eu-exit-and-uk-law.html')


def legislature_eu(request):
    return render(request, 'new_theme/explore_collection/explore-legislation-originating-from-the-eu.html')


def research_tools(request):
    return render(request, 'new_theme/research-tools.html')


def help_guide(request):
    return render(request, 'new_theme/help_guide/help-and-guide.html')


def how_legislation_work(request):
    return render(request, 'new_theme/help_guide/how-legislation-work.html')


def revised_legislation(request):
    return render(request, 'new_theme/help_guide/revised-legislation.html')


def secondary_legislation(request):
    return render(request, 'new_theme/help_guide/secondary-legislation.html')


def whats_new(request):
    return render(request, 'new_theme/whats_new/whats_new.html')


def new_legislation(request):
    return render(request, 'new_theme/whats_new/new-legislation.html')


def new_legislation_feeds(request):
    return render(request, 'new_theme/whats_new/new-legislation-feeds.html')
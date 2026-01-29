
from collections import defaultdict
import datetime
import json
import os

from django.conf import settings
from django.core.cache import caches
from django.shortcuts import render

from lgu2.util.links import make_contents_link_for_list_entry
# from django.views.decorators.cache import cache_page

from ..api import documents as api
from ..api.doc_types import get_types, Response
from ..api.dates import get_recently_published_dates
from ..api.wagtail_api import get_wagtail_content
from ..api.health_check import check_health
from lgu2.util.labels import get_singular_type_label, get_long_type_label, get_type_label
from django.http import JsonResponse

local_cache = caches["localfile"]


# @cache_page(60 * 15)
def homepage(request):
    data = api.get_new()
    for doc in data['documents'][:5]:
        doc['typeLabel'] = get_singular_type_label(doc['longType'])
        doc['link'] = make_contents_link_for_list_entry(doc)

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
    url = "pages/7/"
    api_data = get_wagtail_content(url)
    return render(request, 'new_theme/help_guide/revised-legislation.html', {"data": api_data})


def secondary_legislation(request):
    url = "pages/8/"
    api_data = get_wagtail_content(url)
    return render(request, 'new_theme/help_guide/secondary-legislation.html', {"data": api_data})


def whats_new(request):
    return render(request, 'new_theme/whats_new/whats_new.html')


def group_documents_for_new_legislation_page(docs):
    groups = defaultdict(list)
    for doc in docs:
        groups[doc['longType']].append(doc)
    ordered = sorted(groups.items(), key=lambda item: len(item[1]), reverse=True)
    return [
        {
            'longType': lt,
            'label': get_type_label(lt),
            'documents': group_docs
        }
        for lt, group_docs in ordered
    ]


def new_legislation(request, country=None, date=None):
    dates = local_cache.get_or_set('recently_published_dates', get_recently_published_dates, 3600)
    date = dates[0]['date'] if date is None else datetime.date.fromisoformat(date)
    data = api.get_published_on(date.isoformat(), country)
    for doc in data['documents']:
        doc['link'] = make_contents_link_for_list_entry(doc)
    document_groups = group_documents_for_new_legislation_page(data['documents'])
    context = {
        'country': country,
        'date': date,
        'dates': dates,
        'document_groups': document_groups
    }
    return render(request, 'new_theme/whats_new/new-legislation.html', context)


def new_legislation_feeds(request):
    return render(request, 'new_theme/whats_new/new-legislation-feeds.html')


def about_us(request):
    return render(request, 'new_theme/about_us/about_us.html')


def health_dependencies(request):
    try:
        response = check_health()

        if response.status_code == 200:
            return JsonResponse(
                {
                    "status": "ok",
                    "checks": {
                        "api": "ok"
                    }
                },
                status=200
            )

        # Spring responded but unhealthy
        return JsonResponse(
            {
                "status": "unhealthy",
                "checks": {
                    "api": "unhealthy"
                }
            },
            status=503
        )

    except Exception:
        # Spring is unreachable / timeout / network error
        return JsonResponse(
            {
                "status": "unhealthy",
                "checks": {
                    "api": "down"
                }
            },
            status=503
        )
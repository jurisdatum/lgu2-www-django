
import asyncio
from datetime import datetime
from itertools import zip_longest

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.template import loader

from . import api
from .models import Message, DatasetCompleteness

def index(request):
    return redirect('browse')

def hello(request):
    return HttpResponse("Hello world!")

def group_counts_for_timeline(yearly_counts, complete_cutoff):

    yearly_counts = list(reversed(yearly_counts))
    first_year = yearly_counts[0]['year']

    # mark complete or partial
    for count in yearly_counts:
        count['complete'] = count['year'] >= complete_cutoff

    # calclulate no_data_for_prev_yrs
    next_expected_year = (first_year // 10) * 10
    for count in yearly_counts:
        count['no_data_for_prev_yrs'] = count['year'] - next_expected_year
        next_expected_year = count['year'] + 1

    # group by decade
    last_decade = (first_year // 10) - 1
    this_year = datetime.now().year
    grouped = []
    for count in yearly_counts:
        year = count['year']
        decade = year // 10
        if decade != last_decade:
            first_year_of_decade = (year // 10) * 10
            last_year_of_decade = first_year_of_decade + 9
            if last_year_of_decade > this_year:
                last_year_of_decade = this_year
            group = { 'first_year': first_year_of_decade, 'last_year': last_year_of_decade, 'counts': [] }
            grouped.append(group)
            last_decade = decade
        grouped[-1]['counts'].append(count)
    return grouped

def browse(request, year = None):
    page = request.GET.get('page', '1')
    if year is None:
        data = api.browse_by_type('ukpga', page)
    else:
        data = api.browse_by_type_and_year('ukpga', year, page)

    for doc in data['documents']:
        if doc['version'] == 'enacted':
            doc['link'] = doc['id'] + '/' + doc['version']
        else:
            doc['link'] = doc['id']

    yearly_counts = data['meta']['counts']['yearly']
    last_year = yearly_counts[0]['year']
    first_year = yearly_counts[-1]['year']
    complete_cutoff = DatasetCompleteness.objects.get(type='ukpga').cutoff

    grouped_yearly_counts = zip_longest(*(iter(yearly_counts),) * 24) # for yearPagination

    grouped_by_decade = group_counts_for_timeline(yearly_counts, complete_cutoff)
    timeline_style = "<style type=\"text/css\">#timeline #timelineData {{ width: {w}em }}</style>".format(w=str(len(grouped_by_decade) * 35))

    page = int(page)
    last_page = int(data['meta']['totalPages'])
    first_page_number_to_show = 1 if page < 10 else page - 9
    last_page_number_to_show = last_page if last_page < page + 9 else page + 9
    page_numbers = range(first_page_number_to_show, last_page_number_to_show + 1)
    context = {
        'documents': data['documents'],
        'total': data['meta']['counts']['total'],
        'grouped_yearly_counts': grouped_yearly_counts,
        'years': {
            'first': first_year,
            'first_complete': complete_cutoff,
            'last': last_year if last_year < datetime.now().year else None
        },
        'decade_groups_for_timeline': grouped_by_decade,
        'timeline_style': timeline_style,
        'page_numbers': page_numbers,
        'current_page': page,
        'last_page': last_page,
        'search_endpoint': '/ukpga' if year is None else '/ukpga/' + str(year),
        'page_last_modified': data['meta']['updated'][:10]
    }
    template = loader.get_template('browse/browse.html')
    return HttpResponse(template.render(context, request))


# documents

def make_timeline_data(meta, pit):

    min_list_width = 717
    max_item_width = 637
    min_item_width = 142

    versions = meta['versions']
    versions = filter(lambda v: v != 'enacted', versions)
    versions = filter(lambda v: v != 'prospective', versions) # ?
    versions = sorted(versions)
    versions = list(map(lambda v: { 'date': v }, versions))

    if not versions:
        return None
    elif len(versions) == 1:
        item_width = max_item_width
    elif len(versions) > 4: # 5?
        item_width = min_item_width
    else:
        item_width = int((min_list_width - 50) / len(versions))
    list_width = len(versions) * item_width + 50
    if list_width < min_list_width:
        list_width = min_list_width

    for version in versions:
        date = datetime.strptime(version['date'], '%Y-%m-%d')
        version['label'] = date.strftime("%d/%m/%Y")
        version['width'] = item_width
        version['current'] = version['date'] == meta['version']
    versions[-1]['width'] = item_width - 40
    return {
        'width': list_width,
        'versions': versions,
        'scroll': list_width > min_list_width
    }

def document(request, type, year, number, version=None):

    data = api.get_document(type, year, number, version)

    if 'error' in data:
        template = loader.get_template('404.html')
        return HttpResponseNotFound(template.render({}, request))

    if version is None and data['meta']['status'] == 'final':
        return redirect('document-version', type=type, year=year, number=number, version='enacted')

    if version:
        data['meta']['link'] = '/' + data['meta']['id'] + '/' + version
    else:
        data['meta']['link'] = '/' + data['meta']['id']

    try:
        version_date = datetime.strptime(version, '%Y-%m-%d')
        pit = version_date.strftime("%d/%m/%Y")
    except:
        pit = None

    timeline = make_timeline_data(data['meta'], pit)

    if data['meta']['status'] == 'final':
        status_message = Message.objects.get(name='status_warning_original_version').text
    elif pit:
        status_message = 'Point in time view as at ' + pit + '.'
    else:
        status_message = None

    template = loader.get_template('document/document.html')
    context = {
        'meta': data['meta'],
        'pit': pit,
        'timeline': timeline,
        'status_message': status_message,
        'article': data['html']
    }
    return HttpResponse(template.render(context, request))

def document_clml(request, type, year, number, version=None):
    clml = api.get_clml(type, year, number, version)
    return HttpResponse(clml, content_type='application/xml')

def document_akn(request, type, year, number, version=None):
    akn = api.get_akn(type, year, number, version)
    return HttpResponse(akn, content_type='application/xml')


# metadata

def metadata(request, type, year, number):
    data = api.get_metadata(type, year, number)
    template = loader.get_template('metadata/metadata.html')
    context = { 'item': data }
    return HttpResponse(template.render(context, request))


# combined

async def get_document_async(type, year, number):
    return api.get_document(type, year, number)

async def get_metadata_async(type, year, number):
    return api.get_metadata(type, year, number)

async def combined(request, type, year, number):
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(get_document_async(type, year, number))
        task2 = tg.create_task(get_metadata_async(type, year, number))
    data = await task1
    meta = await task2
    template = loader.get_template('metadata/combined.html')
    context = { 'meta1': data['meta'], 'meta2': { 'item': meta } }
    return HttpResponse(template.render(context, request))

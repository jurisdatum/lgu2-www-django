
from datetime import datetime
from itertools import zip_longest

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from . import api

def index(request):
    return redirect('ukpga')

def hello(request):
    return HttpResponse("Hello world!")

def group_counts_for_timeline(yearly_counts):

    yearly_counts = list(reversed(yearly_counts))
    first_year = yearly_counts[0]['year']

    # mark complete or partial
    complete_cutoff = 1988
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

def browse(request):
    page = request.GET.get('page', '1')
    data = api.browse_by_type('ukpga', page)
    yearly_counts = data['meta']['counts']['yearly']
    grouped_yearly_counts = zip_longest(*(iter(yearly_counts),) * 24) # for yearPagination
    grouped_by_decade = group_counts_for_timeline(yearly_counts)
    timeline_style = "<style type=\"text/css\">#timeline #timelineData {{ width: {w}em }}</style>".format(w=str(len(grouped_by_decade) * 35))

    page = int(page)
    first_page = 1 if page < 10 else page - 9
    last_page = page if len(data['documents']) < 20 else page + 9
    print('last page', last_page)
    page_numbers = range(first_page, last_page + 1)
    print('page numbers', page_numbers)

    context = {
        'documents': data['documents'],
        'total': data['meta']['counts']['total'],
        'grouped_yearly_counts': grouped_yearly_counts,
        'decade_groups_for_timeline': grouped_by_decade,
        'timeline_style': timeline_style,
        'page_numbers': page_numbers,
        'current_page': page
    }
    template = loader.get_template('browse.html')
    return HttpResponse(template.render(context, request))


def document(request, type = 'ukpga', year = 2018, number = 1):
    article = api.get_document(type, year, number)
    template = loader.get_template('document.html')
    context = { 'article': article }
    return HttpResponse(template.render(context, request))


from datetime import datetime
from itertools import zip_longest

from django.http import HttpResponse
from django.template import loader
from django.urls import reverse

from ..api.browse import browse_by_type, browse_by_type_and_year
from ..models import DatasetCompleteness

def _group_counts_for_timeline(yearly_counts, complete_cutoff):

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
        data = browse_by_type('ukpga', page)
    else:
        data = browse_by_type_and_year('ukpga', year, page)

    link_prefix = '/cy' if request.LANGUAGE_CODE == 'cy' else ''
    for doc in data['documents']:
        if doc['version'] == 'enacted':
            doc['link'] = link_prefix + doc['id'] + '/contents/' + doc['version']
        else:
            doc['link'] = link_prefix + doc['id'] + '/contents'

    yearly_counts = data['meta']['counts']['yearly']
    last_year = yearly_counts[0]['year']
    first_year = yearly_counts[-1]['year']
    complete_cutoff = DatasetCompleteness.objects.get(type='ukpga').cutoff

    grouped_yearly_counts = zip_longest(*(iter(yearly_counts),) * 24) # for yearPagination

    grouped_by_decade = _group_counts_for_timeline(yearly_counts, complete_cutoff)
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
        'search_endpoint': reverse('browse') if year is None else reverse('browse-year', args=[year]),
        # 'page_last_modified': data['meta']['updated'][:10]
    }
    template = loader.get_template('browse/browse.html')
    return HttpResponse(template.render(context, request))

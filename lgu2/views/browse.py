
from datetime import datetime
from itertools import zip_longest
import string
from typing import Optional

from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse

from ..api.browse import browse_by_type, browse_by_type_and_year
from ..util.cutoff import get_cutoff
from ..util.labels import get_type_label
from ..util.types import to_short_type


def _group_counts_for_timeline(yearly_counts, complete_cutoff: Optional[int]):

    yearly_counts = list(reversed(yearly_counts))
    first_year = yearly_counts[0]['year']

    # mark complete or partial
    for count in yearly_counts:
        count['complete'] = False if complete_cutoff is None else count['year'] >= complete_cutoff

    # calclulate no_data_for_prev_yrs
    next_expected_year = (first_year // 10) * 10
    for count in yearly_counts:
        prev_yrs = count['year'] - next_expected_year
        mod = count['year'] % 10
        count['no_data_for_prev_yrs'] = mod if mod < prev_yrs else prev_yrs
        next_expected_year = count['year'] + 1

    # add class
    max_yearly_count = max(map(lambda y: y['count'], yearly_counts))
    for count in yearly_counts:
        class_1 = 'per' + '{:02d}'.format(count['count'] * 100 // max_yearly_count)
        class_2 = 'complete' if count['complete'] else 'partial'
        class_3 = 'noDataforPrev' + str(count['no_data_for_prev_yrs']) + 'yrs'
        count['class'] = ' '.join((class_1, class_2, class_3))

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
            group = {'first_year': first_year_of_decade, 'last_year': last_year_of_decade, 'counts': []}
            grouped.append(group)
            last_decade = decade
        grouped[-1]['counts'].append(count)
    return grouped


def browse(request, type, year=None):
    page = request.GET.get('page', '1')
    if year is None:
        data = browse_by_type(type, page)
    else:
        data = browse_by_type_and_year(type, year, page)

    for by_type in data['meta']['counts']['byType']:
        by_type['label'] = get_type_label(by_type['type'])
        short_type = to_short_type(by_type['type'])
        by_type['link'] = reverse('browse', args=[short_type]) if year is None else reverse('browse-year', args=[short_type, year])

    link_prefix = '/cy' if request.LANGUAGE_CODE == 'cy' else ''
    for doc in data['documents']:
        if doc['version'] == 'enacted':
            doc['link'] = link_prefix + '/' + doc['id'] + '/contents/' + doc['version']
        elif doc['version'] == 'made':
            doc['link'] = link_prefix + '/' + doc['id'] + '/contents/' + doc['version']
        else:
            doc['link'] = link_prefix + '/' + doc['id'] + '/contents'
        doc['label'] = get_type_label(doc['longType'])

    yearly_counts = data['meta']['counts']['byYear']
    last_year = yearly_counts[0]['year']
    first_year = yearly_counts[-1]['year']
    complete_cutoff = get_cutoff(type)

    # add links
    for count in yearly_counts:
        count['link'] = reverse('browse-year', args=[type, count['year']])

    grouped_yearly_counts = zip_longest(*(iter(yearly_counts),) * 24)  # for yearPagination

    grouped_by_decade = _group_counts_for_timeline(yearly_counts, complete_cutoff)
    timeline_style = "<style type=\"text/css\">#timeline #timelineData {{ width: {w}em }}</style>".format(w=str(len(grouped_by_decade) * 35))

    page = int(page)
    last_page = int(data['meta']['totalPages'])
    first_page_number_to_show = 1 if page < 10 else page - 9
    last_page_number_to_show = last_page if last_page < page + 9 else page + 9
    page_numbers = range(first_page_number_to_show, last_page_number_to_show + 1)

    # subjects
    subject_initials = None
    if 'bySubjectInitial' in data['meta']['counts']:  # should not be present and None
        subject_initials = set([i['initial'] for i in data['meta']['counts']['bySubjectInitial']])

    context = {
        'all_lowercase_letters': string.ascii_lowercase,
        'subject_initials': subject_initials,
        'short_type': type,
        'year': year,
        'type_label_plural': get_type_label(type),
        'documents': data['documents'],
        'total': data['meta']['counts']['total'],
        'counts_by_type': data['meta']['counts']['byType'],
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
        'search_endpoint': reverse('browse', args=[type]) if year is None else reverse('browse-year', args=[type, year])
        # 'page_last_modified': data['meta']['updated'][:10]
    }
    template = loader.get_template('browse/browse.html')
    return HttpResponse(template.render(context, request))


def data(request, type: str, format: str, year: Optional[str] = None):
    page = request.GET.get('page', '1')
    if format == 'feed':
        pass  # ToDo
    if format == 'json':
        if year is None:
            data = browse_by_type(type, page)
        else:
            data = browse_by_type_and_year(type, year, page)
        return JsonResponse(data)
    return HttpResponse(status=406)

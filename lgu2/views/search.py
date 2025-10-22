import re
import string
from urllib.parse import urlencode
from collections import defaultdict
from typing import TypedDict, Optional, List, Dict, Any

from django.shortcuts import render, redirect
from django.urls import reverse

from ..api.search import basic_search
from ..api.search_types import SearchParams
from ..api.browse_types import DocEntry
from ..util.cutoff import get_cutoff
from ..util.types import to_short_type
from ..util.version import is_first_version, get_first_version
from ..util.labels import get_type_label


class SearchResultContext(TypedDict):
    meta_data: Dict[str, Any]
    documents_data: List[Any]
    grouped_documents: Optional[Dict[str, List[Any]]]
    page_range: range
    current_page: int
    total_pages: int
    current_subject: Optional[str]
    subject_heading: Optional[str]
    total_count_by_type: int
    total_count_by_year: int
    modified_query_links: Dict[str, str]
    query_params: str
    query_param: SearchParams
    by_year_pagination_count: int
    current_year: str
    current_type: Optional[str]
    grouped_by_decade: bool
    subject_initials: Optional[set[str]]
    all_lowercase_letters: str
    default_pagesize: int


def browse(request, type: str, year: Optional[str] = None):
    params: SearchParams = { 'type': type }
    if year is not None:
        params['year'] = int(year)
    if 'page' in request.GET and request.GET['page'].isdigit():
        params['page'] = int(request.GET['page'])
    if 'pageSize' in request.GET and request.GET['pageSize'].isdigit():
        params['pageSize'] = int(request.GET['pageSize'])
    return search_results_helper(request, params)


def extract_query_params(request) -> SearchParams:
    params: SearchParams = {}

    if "sort" in request.GET and request.GET["sort"].strip():
        params["sort"] = request.GET["sort"].strip()

    if "pageSize" in request.GET and request.GET["pageSize"].isdigit():
        params["pageSize"] = int(request.GET["pageSize"])

    if "page" in request.GET and request.GET["page"].isdigit():
        params["page"] = int(request.GET["page"])

    if "subject" in request.GET and request.GET["subject"].strip():
        params["subject"] = request.GET["subject"].strip()

    if "year" in request.GET and request.GET["year"].isdigit():
        params["year"] = int(request.GET["year"])

    if "type" in request.GET and request.GET["type"].strip():
        params["type"] = request.GET["type"].strip()

    if "title" in request.GET and request.GET["title"].strip():
        params["title"] = request.GET["title"].strip()

    if "number" in request.GET and request.GET["number"].strip():
        params["number"] = request.GET["number"].strip()

    return params


TYPE = r'^(?:[a-z]{3,5}|primary|secondary|primary\+secondary|eu-origin)$'

def build_browse_url_if_possible(params: SearchParams) -> Optional[str]:
    """Build browse URL if params qualify for clean URL routing, None otherwise."""
    if ('type' in params and
        set(params).issubset({'type', 'year', 'page', 'pageSize'}) and
        re.match(TYPE, params['type'])):

        year = params.get('year')
        if year:
            base = reverse('browse-year', kwargs={'type': params['type'], 'year': year})
        else:
            base = reverse('browse', kwargs={'type': params['type']})

        query = {k: params[k] for k in ('page', 'pageSize') if k in params}
        return f"{base}?{urlencode(query, doseq=True)}" if query else base

    return None

def make_smart_link(params: SearchParams):
    browse_url = build_browse_url_if_possible(params)
    return browse_url or f"{ reverse('search') }?{ urlencode(params, doseq=True) }"


def replace_param_and_make_smart_link(params: SearchParams, key: str, value):
    new_params = params.copy()
    new_params[key] = value
    new_params.pop('page', None)
    new_params.pop('pageSize', None)
    return make_smart_link(new_params)


def search_results(request):
    params: SearchParams = extract_query_params(request)
    # redirect to browse URL if possible
    browse_url = build_browse_url_if_possible(params)
    if browse_url:
        return redirect(browse_url)
    return search_results_helper(request, params)


def search_results_helper(request, query_params: SearchParams):

    if query_params.get('type', '').strip() == 'all':
        del query_params['type']

    # Step 2: Fetch data using cleaned parameters
    api_data_raw = basic_search(query_params)

    meta = api_data_raw["meta"]
    documents_data = api_data_raw["documents"]

    # Step 3: Count totals
    total_count_by_type = sum(item["count"] for item in meta.get("counts", {}).get("byType", []))  # type: ignore
    total_count_by_year = sum(item["count"] for item in meta.get("counts", {}).get("byYear", []))  # type: ignore

    # Step 4: Pagination
    current_page = meta.get("page", 1)
    total_pages = meta.get("totalPages", 1)

    if total_pages <= 10:
        page_range = range(1, total_pages + 1)
    else:
        start = max(1, current_page - 5)
        end = min(total_pages, start + 9)
        page_range = range(start, end + 1)

    # Step 5: Generate "remove filter" links using smart link generation
    modified_query_links = {}
    for filter_key in query_params.keys():
        params_without_filter_key = query_params.copy()
        params_without_filter_key.pop(filter_key, None)
        modified_query_links[filter_key] = make_smart_link(params_without_filter_key)

    # Step 6: Base query string
    query_dict = request.GET.copy()
    query_dict.pop("page", None)
    base_query = urlencode(query_dict)

    # Step 7: Filters
    current_year = str(query_params.get("year", ""))
    current_type = query_params.get("type")
    current_subject = query_params.get("subject")
    subject_heading = current_subject if current_subject and len(current_subject) > 1 else None
    current_subject = current_subject[0] if current_subject else None

    default_pagesize = query_params.get("pageSize", 20)

    # Step 8: Grouping by decade (if applicable)
    grouped_by_decade = False
    if len(meta.get("counts", {}).get("byType", [])) == 1:
        grouped_by_decade = group_by_decade(meta["counts"]["byYear"], current_type)

    # Step 8.5 Add links

    if grouped_by_decade:
        for years in grouped_by_decade.values():
            for item in years:
                item['link'] = replace_param_and_make_smart_link(query_params, 'year', item['year'])

    for byType in meta['counts']['byType']:
        byType['link'] = replace_param_and_make_smart_link(query_params, 'type', to_short_type(byType['type']))

    for byYear in meta['counts']['byYear']:
        byYear['link'] = replace_param_and_make_smart_link(query_params, 'year', byYear['year'])

    for byInitial in meta['counts']['bySubjectInitial']:
        byInitial['link'] = replace_param_and_make_smart_link(query_params, 'subject', byInitial['initial'])

    for doc in documents_data:
        kw = DocEntry.parse_id(doc['id'])
        # Welsh versions?
        if is_first_version(doc['version']):
            kw['version'] = doc['version']
            doc['link'] = reverse("toc-version", kwargs=kw)
        else:
            doc['link'] = reverse("toc", kwargs=kw)
        # doc['label'] = get_type_label(doc['longType'])

    # Step 9: Subject initials and links
    subject_initials = None
    if "bySubjectInitial" in meta.get("counts", {}):
        subject_initials = set(i["initial"] for i in meta["counts"]["bySubjectInitial"])

    subject_initial_links = { byInitial['initial']: byInitial['link'] for byInitial in meta['counts']['bySubjectInitial'] }
    subject_initials_and_links = [
        {   'letter': letter,
            'link': subject_initial_links.get(letter),
            'current': (current_subject.upper() == letter.upper()) if current_subject else False
        }
        for letter in string.ascii_lowercase]

    # Generate subject heading links
    subject_heading_links = []
    for heading in meta.get('subjects', []):
        subject_heading_links.append({
            'name': heading,
            'link': replace_param_and_make_smart_link(query_params, 'subject', heading),
            'current': subject_heading == heading
        })

    # Step 10: Group documents by subject (if filtering by subject)
    grouped_documents = None
    if current_subject:
        grouped_documents = defaultdict(list)
        for doc in documents_data:
            for subject in doc.get("subjects", []):
                grouped_documents[subject].append(doc)
        grouped_documents = dict(grouped_documents)

    # Step 11: Build context
    context: SearchResultContext = {
        "meta_data": meta,
        "documents_data": documents_data,
        "grouped_documents": grouped_documents,
        "page_range": page_range,
        "current_page": current_page,
        "total_pages": total_pages,
        "current_subject": current_subject,
        "subject_heading": subject_heading,
        "total_count_by_type": total_count_by_type,
        "total_count_by_year": total_count_by_year,
        "modified_query_links": modified_query_links,
        "query_params": f"?{base_query}" if base_query else "",
        "query_param": query_params,
        "by_year_pagination_count": len(meta.get("counts", {}).get("byYear", [])),
        "current_year": current_year,
        "current_type": current_type,
        "grouped_by_decade": grouped_by_decade,
        "subject_initials": subject_initials,  # now used only to check for presence of subjects
        "subject_initials_and_links": subject_initials_and_links,
        "subject_heading_links": subject_heading_links,
        "all_lowercase_letters": string.ascii_lowercase,  # no longer need
        "default_pagesize": default_pagesize,
        "type_label_plural": get_type_label(query_params['type']) if 'type' in query_params else 'documents',
        "type_made_verb": get_first_version(query_params['type']) if 'type' in query_params else 'documents'
    }

    return render(request, "new_theme/search_result/search_result.html", context)


def group_by_decade(year_data, doc_type):
    """
    Groups year data into decades with padding for missing years.
    """
    cut_off = get_cutoff(doc_type)
    grouped = defaultdict(dict)

    # Fill in available year data
    for entry in year_data:
        year = entry["year"]
        count = entry["count"]
        complete = cut_off is not None and year > cut_off

        decade_start = (year // 10) * 10
        decade_label = f"{decade_start}-{decade_start + 9}"

        grouped[decade_label][year] = {
            "year": year,
            "count": count,
            "complete": complete
        }

    # Pad missing years with placeholders
    filled_grouped = {}
    for decade_label, years in grouped.items():
        decade_start = int(decade_label.split("-")[0])
        full_years = []
        for year in range(decade_start, decade_start + 10):
            if year in years:
                full_years.append(years[year])
            else:
                full_years.append({
                    "year": year,
                    "count": 0,
                    "complete": False,
                    "no_data": True
                })
        filled_grouped[decade_label] = full_years

    return dict(sorted(filled_grouped.items()))  # ascending order

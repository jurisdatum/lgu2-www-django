
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, re_path
from django.http import JsonResponse
from .views.robots import robots_txt
from .views.doc_types import list_uk

from .views.browse import data as browse_data
from .views.document import document, data as document_data
from .views import toc
from .views import fragment
from .views.changes.intro import intro as changes_intro
from .views.changes.results import affected as changes_affected, affecting as changes_affecting, both as changes_both
from .views.general import (
    homepage, explore_collection,
    different_legislature, different_legislature_by_country,
    legislature_eu, legislature_eu_exit_uk_law, research_tools,
    help_guide, how_legislation_work, revised_legislation, secondary_legislation,
    whats_new, new_legislation, new_legislation_feeds,
    about_us
)
from .views.search import  browse, search_results
from .views.advance_search import advance_search, extent_search, point_in_time_search, draft_search, impact_search
# urlpatterns = i18n_patterns(
#     path('', lambda r: redirect('browse-uk'), name='home'), prefix_default_language=False
# )

VALID_TYPES = [
    # Primary
    "all", "primary\+secondary", "primary", "ukpga", "ukla", "ukppa", "asp", "asc", "anaw", "mwa", "ukcm", "nia", 
    "aosp", "aep", "aip", "apgb", "gbla", "gbppa", "nisi", "mnia", "apni",
    # Secondary
    "secondary", "uksi", "wsi", "ssi", "nisr", "ukci", "ukmd", "ukmo", "uksro", "nisro",
    # EU
    "eu-origin", "eu", "eur", "eudn", "eudr", "eut", "ukia"
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path("robots.txt", robots_txt),
    path("health", lambda request: JsonResponse({"status": "ok"}))
]

# needed because some JavaScript files add links to "/static/..."
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(.*)$', lambda r, p: redirect(f"{settings.STATIC_URL}{p}"))
    ]

COUNTRY = r'(?P<country>uk|wales|scotland|ni)'
TYPE = r'(?P<type>(?:' + '|'.join(VALID_TYPES) + r')(?:\+(?:' + '|'.join(VALID_TYPES) + r'))*)'
YEAR4 = r'(?P<year>[0-9]{4})'  # a four-digit calendar year
YEAR = r'(?P<year>[0-9]{4}|[A-Z][A-Za-z0-9]+/[0-9-]+)'  # calendar or regnal
NUMBER = r'(?P<number>[0-9]+)'
SECTION = r'(?P<section>[A-Za-z0-9/-]+?)'  # not sure about ? on the end
DATE = r'(?P<date>\d{4}-\d{2}-\d{2})'
VERSION = r'(?P<version>enacted|made|created|adopted|prospective|\d{4}-\d{2}-\d{2})'
LANG = r'(?P<lang>english|welsh)'
DATA = r'data\.(?P<format>xml|akn|html|json|feed)'

urlpatterns += i18n_patterns(
    path('', homepage, name='homepage'),

    # TODO: Remove trailing slash from search and explore URLs
    path('search/', search_results, name='search'),

    path('advance-search', advance_search, name='advance-search'),
    path('search/extent', extent_search, name='extent-search'),
    path('search/point-in-time', point_in_time_search, name='point-in-time-search'),
    path('search/draft-legislation', draft_search, name='draft-legislation-search'),
    path('search/impacts', impact_search, name='impacts-search'),
    
    path('explore/', explore_collection, name='explore'),
    path('explore/legislatures', different_legislature, name='different-legislatures'),
    re_path(fr'^explore/legislatures/{COUNTRY}', different_legislature_by_country, name='different-legislatures-country'),
    path('explore-eu-exit-and-uk-law', legislature_eu_exit_uk_law, name='explore-eu-exit-and-uk-law'),
    path('explore/legislatures/eu', legislature_eu, name='legislatures-eu'),

    path('research-tools/', research_tools, name='research-tools'),
    path('about-us/', about_us, name='about-us'),
    
    path('whats-new/', whats_new, name='whats-new'),
    path('new', new_legislation, name='new-legislation'),
    re_path(fr'^new/{COUNTRY}$', new_legislation),
    re_path(fr'^new/{DATE}$', new_legislation),
    re_path(fr'^new/{COUNTRY}/{DATE}$', new_legislation),
    path('new-legislation-feeds/', new_legislation_feeds, name='new-legislation-feeds'),
    
    path('help/', help_guide, name='help'),
    path('help-how-legislation-works/', how_legislation_work, name='how-legislation-works'),
    path('help-revised-legislation/', revised_legislation, name='revised-legislation'),
    path('help-secondary-legislation', secondary_legislation, name='secondary-legislation'),
    
    path('browse', lambda r: redirect('browse-uk')),
    path('browse/uk', list_uk, name='browse-uk'),

    # browse
    re_path(fr'^{TYPE}$', browse, name='browse'),
    re_path(fr'^{TYPE}/{DATA}$', browse_data),
    re_path(fr'^{TYPE}/{YEAR4}$', browse, name='browse-year'),
    re_path(fr'^{TYPE}/{YEAR4}/{DATA}$', browse_data),
    re_path(fr'^{TYPE}/(?P<subject>[a-z])$', browse, name='browse-subject'),
    re_path(fr'^{TYPE}/{YEAR4}/(?P<subject>[a-z])$', browse, name='browse-year-subject'),

    # documents
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}$', document, name='document'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{DATA}$', document_data, name='document-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{LANG}$', document, name='document-lang'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{LANG}/{DATA}$', document_data, name='document-lang-data'),

    # document versions
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}$', document, name='document-version'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}/{DATA}$', document_data, name='document-version-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}/{LANG}$', document, name='document-version-lang'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}/{LANG}/{DATA}$', document_data, name='document-version-lang-data'),

    # tables of contents
    # FixMe this needs /? on the end and I don't know why
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/?$', toc.toc, name='toc'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{DATA}$', toc.data, name='toc-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{LANG}$', toc.toc, name='toc-lang'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{LANG}/{DATA}$', toc.data, name='toc-lang-data'),

    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{VERSION}$', toc.toc, name='toc-version'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{VERSION}/{DATA}$', toc.data, name='toc-version-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{VERSION}/{LANG}$', toc.toc, name='toc-version-lang'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{VERSION}/{LANG}/{DATA}$', toc.data, name='toc-version-lang-data'),


    # document fragments (sections)
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}/{LANG}$', fragment.fragment, name='fragment-version-lang'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}/{LANG}/{DATA}$', fragment.data, name='fragment-version-lang-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{LANG}$', fragment.fragment, name='fragment-lang'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{LANG}/{DATA}$', fragment.data, name='fragment-lang-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}$', fragment.fragment, name='fragment-version'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}/{DATA}$', fragment.data, name='fragment-version-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}$', fragment.fragment, name='fragment'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{DATA}$', fragment.data, name='fragment-data'),


    # changes
    re_path(r'^changes$', changes_intro, name='changes-intro'),
    re_path(
        r'^changes/affected(?:/(?P<type>[a-z]{3,5}))(?:/(?P<year>[0-9]{4}|\*))?(?:/(?P<number>[0-9]+))?(?:/data\.(?P<format>json|feed))?$',
        changes_affected, name='changes-affected'),
    re_path(
        r'^changes/affecting(?:/(?P<type>[a-z]{3,5}))(?:/(?P<year>[0-9]{4}|\*))?(?:/(?P<number>[0-9]+))?(?:/data\.(?P<format>json|feed))?$',
        changes_affecting, name='changes-affecting'),
    re_path(
        r'^changes/affected(?:/(?P<type1>[a-z]{3,5}))(?:/(?P<year1>[0-9]{4}|\*))?(?:/(?P<number1>[0-9]+))?/affecting(?:/(?P<type2>[a-z]{3,5}))(?:/(?P<year2>[0-9]{4}|\*))?(?:/(?P<number2>[0-9]+))?(?:/data\.(?P<format>json|feed))?$',
        changes_both, name='changes-both'),

    prefix_default_language=False
)

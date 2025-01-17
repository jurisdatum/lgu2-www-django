
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, re_path, include
from .views.doc_types import list_uk

from .views.browse import browse, data as browse_data
from .views.document import document, data as document_data
from .views import toc
from .views.metadata import metadata, combined
from .views import fragment
from .views.cms_pages import about_us
from wagtail.admin import urls as wagtailadmin_urls 
# from wagtail import urls as wagtailurls

urlpatterns = i18n_patterns(
    path('', lambda r: redirect('browse-uk'), name='home'), prefix_default_language=False
)

urlpatterns += [

    path('admin/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    # path('pages/', include(wagtailurls)),
    # path('hello', lambda r: HttpResponse("Hello world!"), name='hello'),
]

# needed because some JavaScript files add links to "/static/..."
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(.*)$', lambda r, p: redirect(f"{settings.STATIC_URL}{p}"))
    ]

TYPE = r'(?P<type>[a-z]{3,5})'
YEAR4 = r'(?P<year>[0-9]{4})'  # a four-digit calendar year
YEAR = r'(?P<year>[0-9]{4}|[A-Z][A-Za-z0-9]+/[0-9-]+)'  # calendar or regnal
NUMBER = r'(?P<number>[0-9]+)'
SECTION = r'(?P<section>[A-Za-z0-9/-]+?)'  # not sure about ? on the end
VERSION = r'(?P<version>enacted|made|\d{4}-\d{2}-\d{2})'  # ToDo 'created', 'adopted'
LANG = r'(?P<lang>english|welsh)'
DATA = r'data\.(?P<format>xml|akn|html|json)'

urlpatterns += i18n_patterns(

    path('browse', lambda r: redirect('browse-uk')),
    path('browse/uk', list_uk, name='browse-uk'),
    path('about-us/', about_us, name='about-us'),

    re_path(fr'^{TYPE}$', browse, name='browse'),
    re_path(fr'^{TYPE}/{DATA}$', browse_data),
    re_path(fr'^{TYPE}/{YEAR4}$', browse, name='browse-year'),
    re_path(fr'^{TYPE}/{YEAR4}/{DATA}$', browse_data),

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


    # linked data
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/metadata', metadata, name='metadata'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/combined', combined),


    # document fragments (sections)
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}$', fragment.fragment, name='fragment-version'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}/{DATA}$', fragment.data, name='fragment-version-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}$', fragment.fragment, name='fragment'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{DATA}$', fragment.data, name='fragment-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}/{LANG}$', fragment.fragment, name='fragment-version-lang'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}/{LANG}/{DATA}$', fragment.data, name='fragment-version-lang-data'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{LANG}$', fragment.fragment, name='fragment-lang'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{LANG}/{DATA}$', fragment.data, name='fragment-lang-data'),

    prefix_default_language=False
)

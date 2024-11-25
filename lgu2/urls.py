
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path, re_path

from .views.doc_types import list_uk
from .views.browse import browse
from .views.document import document, document_clml, document_akn
from .views import toc
from .views.metadata import metadata, combined
from .views import fragment

urlpatterns = i18n_patterns(

    path('', lambda r: redirect('browse-uk'), name='home'), prefix_default_language=False
)

urlpatterns += [

    path('admin/', admin.site.urls),
    path('hello', lambda r: HttpResponse("Hello world!"), name='hello'),
]

# needed because some JavaScript files add links to "/static/..."
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(.*)$', lambda r, p: redirect(f"{settings.STATIC_URL}{p}"))
    ]

TYPE = r'(?P<type>[a-z]{3,5})'
YEAR = r'(?P<year>[0-9]{4}|[A-Z][A-Za-z0-9]+/[0-9-]+)'
NUMBER = r'(?P<number>[0-9]+)'
SECTION = r'(?P<section>[A-Za-z0-9/-]+?)'  # not sure about ? on the end
VERSION = r'(?P<version>enacted|made|\d{4}-\d{2}-\d{2})'  # ToDo 'created', 'adopted'
LANG = r'(?P<lang>english|welsh)'
DATA = r'data\.(?P<format>xml|akn|json)'

urlpatterns += i18n_patterns(

    path('browse', lambda r: redirect('browse-uk')),
    path('browse/uk', list_uk, name='browse-uk'),
    re_path(r'^(?P<type>[a-z]{3,5})$', browse, name='browse'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})$', browse, name='browse-year'),

    # documents
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}$', document, name='document'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/data\.xml$', document_clml),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/data\.akn$', document_akn),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{LANG}$', document, name='document-lang'),
    # re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{LANG}/data\.xml$', document_clml),
    # re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{LANG}/data\.akn$', document_akn),

    # document versions
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}$', document, name='document-version'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}/data\.xml$', document_clml),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}/data\.akn$', document_akn),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}/{LANG}$', document, name='document-version-lang'),
    # re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}/{LANG}/data\.xml$', document_clml),
    # re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{VERSION}/{LANG}/data\.akn$', document_akn),

    # tables of contents
    # FixMe this needs /? on the end and I don't know why
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/?$', toc.toc, name='toc'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{DATA}$', toc.data),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{LANG}$', toc.toc, name='toc-lang'),
    # re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{LANG}/{DATA}$', toc.data),

    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{VERSION}$', toc.toc, name='toc-version'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{VERSION}/{DATA}$', toc.data),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{VERSION}/{LANG}$', toc.toc, name='toc-version-lang'),
    # re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/contents/{VERSION}/{LANG}/{DATA}$', toc.data),


    # linked data
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/metadata', metadata, name='metadata'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/combined', combined),


    # document fragments (sections)
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}$', fragment.fragment, name='fragment-version'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}/data\.(?P<format>xml|akn)$', fragment.data),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}$', fragment.fragment, name='fragment'),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/data\.(?P<format>xml|akn)$', fragment.data),
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{VERSION}/{LANG}$', fragment.fragment, name='fragment-version-lang'),
    # ToDo data
    re_path(fr'^{TYPE}/{YEAR}/{NUMBER}/{SECTION}/{LANG}$', fragment.fragment, name='fragment-lang'),
    # ToDo data

    prefix_default_language=False
)

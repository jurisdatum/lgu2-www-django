
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

urlpatterns += i18n_patterns(

    path('browse', lambda r: redirect('browse-uk')),
    path('browse/uk', list_uk, name='browse-uk'),
    re_path(r'^(?P<type>[a-z]{3,5})$', browse, name='browse'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})$', browse, name='browse-year'),

    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)$', document, name='document'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/data\.xml$', document_clml),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/data\.akn$', document_akn),

    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<version>enacted|made|\d{4}-\d{2}-\d{2})$', document, name='document-version'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<version>enacted|made|\d{4}-\d{2}-\d{2})/data\.xml$', document_clml),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<version>enacted|made|\d{4}-\d{2}-\d{2})/data\.akn$', document_akn),

    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/contents$', toc.toc, name='document-toc'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/contents/data\.(?P<format>xml|akn|json)$', toc.data),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/contents/(?P<version>enacted|made|\d{4}-\d{2}-\d{2})$', toc.toc, name='document-toc-version'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/contents/(?P<version>enacted|made|\d{4}-\d{2}-\d{2})/data\.(?P<format>xml|akn|json)$', toc.data),

    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/metadata', metadata, name='metadata'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/combined', combined),

    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<section>[A-Za-z0-9/-]+)/(?P<version>enacted|made|\d{4}-\d{2}-\d{2})$', fragment.fragment, name='fragment'),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<section>[A-Za-z0-9/-]+)/(?P<version>enacted|made|\d{4}-\d{2}-\d{2})/data\.(?P<format>xml|akn)$', fragment.data),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<section>[A-Za-z0-9/-]+)$', fragment.fragment),
    re_path(r'^(?P<type>[a-z]{3,5})/(?P<year>[0-9]{4})/(?P<number>[0-9]+)/(?P<section>[A-Za-z0-9/-]+)/data\.(?P<format>xml|akn)$', fragment.data),

    prefix_default_language=False
)

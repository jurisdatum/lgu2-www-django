
from django.http import HttpResponse
from django.shortcuts import redirect

def index(request):
    return redirect('browse')

def hello(request):
    return HttpResponse("Hello world!")

from .browse import browse

from .document import document, document_clml, document_akn

from .metadata import metadata, combined

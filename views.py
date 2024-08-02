
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from .api import browse_by_type

def index(request):
    return redirect('ukpga')

def hello(request):
    return HttpResponse("Hello world!")

def browse(request):
    data = browse_by_type('ukpga')
    template = loader.get_template('browse.html')
    context = { 'documents': data['documents'] }
    return HttpResponse(template.render(context, request))


from itertools import zip_longest

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
    yearly_counts = data['meta']['counts']['yearly']
    grouped_yearly_counts = zip_longest(*(iter(yearly_counts),) * 24)
    template = loader.get_template('browse.html')
    context = { 'documents': data['documents'], 'grouped_yearly_counts': grouped_yearly_counts }
    return HttpResponse(template.render(context, request))

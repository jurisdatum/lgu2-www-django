
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

def index(request):
    return redirect('ukpga')

def hello(request):
    return HttpResponse("Hello world!")

def browse(request):
    template = loader.get_template('browse.html')
    context = {}
    return HttpResponse(template.render(context, request))


from django.http import HttpResponse
from django.shortcuts import redirect

def index(request):
    return redirect('hello')

def hello(request):
    return HttpResponse("Hello world!")

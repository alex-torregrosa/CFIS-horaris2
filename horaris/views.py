from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from .models import Facultad, Carrera
from django.template import loader


def index(request):
    template = loader.get_template('main.template.html')
    data = {
        'carreras_list':  Carrera.objects.all(),
        'facus': Facultad.objects.all()
    }
    return HttpResponse(template.render(data,request))

def mainjs(request):
    template = loader.get_template('main.js')
    data = {
    }
    return HttpResponse(template.render(data,request))

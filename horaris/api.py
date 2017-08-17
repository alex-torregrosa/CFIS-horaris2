from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from .models import Carrera, Facultad, Quatri, Asignatura
import collections


def listFacus(request):
    # Llista en json de les facultats
    facus = Facultad.objects.all()
    v = {}
    for el in facus:
        v[str(el)]=el.id;
    # L'OrderedDict fa que apareguin en ordre alfabetic
    return JsonResponse(collections.OrderedDict(sorted(v.items())))

def listQ(request):
    # Llista en json dels quatris
    facID = int(request.GET.get("f"))
    fac = Facultad.objects.get(pk=facID)
    cuatris = Quatri.objects.filter(facultad=fac)
    v = {}
    for el in cuatris:
        v[str(el)]=el.id;
    return JsonResponse(collections.OrderedDict(sorted(v.items())))

def listCarreras(request):
    # Llista en json de les carreres
    facID = int(request.GET.get("f"))
    fac = Facultad.objects.get(pk=facID)
    carreras = Carrera.objects.filter(facultad=fac)
    v = {}
    for el in carreras:
        v[str(el)]=el.id;
    return JsonResponse(collections.OrderedDict(sorted(v.items())))


def listAsigs(request):
    # Llista en json de les assignatures
    # arguments de la URL
    q = int(request.GET.get("q"))
    carr = int(request.GET.get("c"))
    # Carrega d'objectes
    quat = Quatri.objects.get(pk=q)
    mcarrera = Carrera.objects.get(pk=carr)
    assigs = Asignatura.objects.filter(carrera=mcarrera, cuatri = quat)
    v = {}
    for el in assigs:
        v[str(el)]=el.id;
    return JsonResponse(v)

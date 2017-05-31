from bs4 import BeautifulSoup
import requests
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from .models import Carrera, Facultad, Quatri, Asignatura

def loadCarrerasEtseib(request):
    print("Loading career list... " ,end="")
    r = requests.get("https://guiadocent.etseib.upc.edu/simgen/form/simgen.php?lang=es")

    # r = requests.get("http://localhost:8888/tst.html")
    parsed = BeautifulSoup(r.text,"html.parser")
    print("OK")


    print("Clearing etseib... ",end="")
    try:
        etseib = Facultad.objects.get(name="etseib")
        etseib.delete()
    except Facultad.DoesNotExist:
        pass
    etseib = Facultad(name="etseib")
    etseib.save()
    print("OK")
    ls = parsed.find(attrs={'name':'degree'})
    for child in ls.find_all('option'):
        # print(child["value"],str(child.string))
        carrera = Carrera(name=child.string,codigo=int(child["value"]),facultad=etseib)
        carrera.save()

    ls = parsed.find(attrs={'name':'semester'})
    for child in ls.find_all('option'):
        # print(child["value"],str(child.string))
        quatri = Quatri(name=child.string,codigo=child["value"],facultad=etseib)
        quatri.save()
    return HttpResponse("OK")

def loadEtseibAssigs(request):
    try:
        etseib = Facultad.objects.get(name="etseib")
    except Facultad.DoesNotExist:
        return HttpResponse("ERROR: ETSEIB NOT FOUND")

    cuatris = Quatri.objects.filter(facultad=etseib)
    carrs = Carrera.objects.filter(facultad=etseib)
    for mcuatri in cuatris:
        for mcarrera in carrs:
            r = requests.get("https://guiadocent.etseib.upc.edu/simgen/form/simgen.php?lang=es&degree="+str(mcarrera.codigo)+"&semester="+mcuatri.codigo)
            parsed = BeautifulSoup(r.text,"html.parser")
            print("Downloaded: ",mcuatri, mcarrera)
            asigs = parsed.find_all(attrs={'type':'checkbox'})
            Asignatura.objects.filter(carrera = mcarrera).delete()
            if asigs != None:
                for el in asigs:
                    asignat = Asignatura(name = el.parent.next_sibling.next_sibling.next_sibling.string, carrera = mcarrera,cuatri= mcuatri, codigo = el["name"], codiUPC = el.parent.next_sibling.next_sibling.string,loaded=False)
                    # print(el.parent.next_sibling.next_sibling.next_sibling)
                    asignat.save()
            else:
                print("Nada de nada!")
    return HttpResponse("OK")


def listFacus(request):
    facus = Facultad.objects.all()
    v = {}
    for el in facus:
        v[str(el)]=el.id;
    return JsonResponse(v)

def listQ(request):
    facID = int(request.GET.get("f"))
    fac = Facultad.objects.get(pk=facID)
    cuatris = Quatri.objects.filter(facultad=fac)
    v = {}
    for el in cuatris:
        v[str(el)]=el.id;
    return JsonResponse(v)

def listCarreras(request):
    facID = int(request.GET.get("f"))
    fac = Facultad.objects.get(pk=facID)
    carreras = Carrera.objects.filter(facultad=fac)
    v = {}
    for el in carreras:
        v[str(el)]=el.id;
    return JsonResponse(v)


def listAsigs(request):
    q = int(request.GET.get("q"))
    carr = int(request.GET.get("c"))
    quat = Quatri.objects.get(pk=q)
    mcarrera = Carrera.objects.get(pk=carr)
    assigs = Asignatura.objects.filter(carrera=mcarrera, cuatri = quat)
    v = {}
    for el in assigs:
        v[str(el)]=el.id;
    return JsonResponse(v)

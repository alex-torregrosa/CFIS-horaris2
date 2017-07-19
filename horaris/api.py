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
    # Si existeix la etseib borrala
    try:
        etseib = Facultad.objects.get(name="etseib")
        etseib.delete()
    except Facultad.DoesNotExist:
        # Si no existeix, no petis
        pass
    etseib = Facultad(name="etseib")
    etseib.save()
    print("OK")
    # Busca les carreres
    ls = parsed.find(attrs={'name':'degree'})
    for child in ls.find_all('option'):
        # print(child["value"],str(child.string))
        carrera = Carrera(name=child.string,codigo=int(child["value"]),facultad=etseib)
        carrera.save()
    # Busca els quatris
    ls = parsed.find(attrs={'name':'semester'})
    for child in ls.find_all('option'):
        # print(child["value"],str(child.string))
        quatri = Quatri(name=child.string,codigo=child["value"],facultad=etseib)
        quatri.save()
    # Magic
    return HttpResponse("OK")

def loadEtseibAssigs(request):
    # Carrega la llista d'assignatures per a totes les carreres i quatris de la etseib
    # TODO: Molaria ficar-la a un CRON o similar
    try:
        etseib = Facultad.objects.get(name="etseib")
    except Facultad.DoesNotExist:
        #Si, la has liat una mica parda...
        # potser cridar loadCarrerasEtseib(request)? <- la HttpResponse petaria...
        # Si l'ordre de crida es fa be, aixó no hauria de passar
        return HttpResponse("ERROR: ETSEIB NOT FOUND")

    cuatris = Quatri.objects.filter(facultad=etseib)
    carrs = Carrera.objects.filter(facultad=etseib)
    # Loop doble la mar de maco, lógicament això triga bastant
    # TODO: executar amb channels???
    for mcarrera in carrs:
        # Eliminem totes les assignatures existents
        Asignatura.objects.filter(carrera = mcarrera).delete()

        for mcuatri in cuatris:
            r = requests.get("https://guiadocent.etseib.upc.edu/simgen/form/simgen.php?lang=es&degree="+str(mcarrera.codigo)+"&semester="+mcuatri.codigo)
            parsed = BeautifulSoup(r.text,"html.parser")
            print("Downloaded: ",mcuatri, mcarrera)
            asigs = parsed.find_all(attrs={'type':'checkbox'})

            if asigs != None:
                for el in asigs:
                    # Creació de les assignatures
                    asignat = Asignatura(name = el.parent.next_sibling.next_sibling.next_sibling.string, carrera = mcarrera,cuatri= mcuatri, codigo = el["name"], codiUPC = el.parent.next_sibling.next_sibling.string,loaded=False)
                    # print(el.parent.next_sibling.next_sibling.next_sibling)
                    asignat.save()
            else:
                # Aquesta gent de la etseib que no penja assignatures...
                print("No se han encontrado asignaturas")
    # Com no,
    return HttpResponse("OK")


def listFacus(request):
    # Llista en json de les facultats
    facus = Facultad.objects.all()
    v = {}
    for el in facus:
        v[str(el)]=el.id;
    return JsonResponse(v)

def listQ(request):
    # Llista en json dels quatris
    facID = int(request.GET.get("f"))
    fac = Facultad.objects.get(pk=facID)
    cuatris = Quatri.objects.filter(facultad=fac)
    v = {}
    for el in cuatris:
        v[str(el)]=el.id;
    return JsonResponse(v)

def listCarreras(request):
    # Llista en json de les carreres
    facID = int(request.GET.get("f"))
    fac = Facultad.objects.get(pk=facID)
    carreras = Carrera.objects.filter(facultad=fac)
    v = {}
    for el in carreras:
        v[str(el)]=el.id;
    return JsonResponse(v)


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

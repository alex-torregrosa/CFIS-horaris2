import requests, json
from bs4 import BeautifulSoup
from django.http import HttpResponse
from ..models import Carrera, Facultad, Quatri, Asignatura, Grupo

# aplicatiu horaris telecos https://infoteleco.upc.edu/documents/gdqpgt75.html --> mirar urls i parametres a fitxer JS (app - gh_simul)

def loadCarreras(request):
    print("Loading career list... ", end="")
    r = requests.get("https://infoteleco.upc.edu/documents/gdqpgt75.html")

    parsed = BeautifulSoup(r.text, "html.parser")
    print("OK")

    print("Clearing etsetb... ", end="")
    try:
        etsetb = Facultad.objects.get(name="etsetb")
        etsetb.delete()
    except Facultad.DoesNotExist:
        pass

    etsetb = Facultad(name="etsetb")
    etsetb.save()
    print("OK")


    ls = parsed.find(attrs={'name': 'selPla'})
    for child in ls.find_all('option'):
        #print(child["value"], str(child.string))
        carrera = Carrera(name=child.string, codigo=child["value"], facultad=etsetb)
        carrera.save()

    ls = parsed.find(attrs={'name':'gh_sel_sem'})
    for child in ls.find_all('option'):
        #print(child["value"], str(child.string))
        quatri = Quatri(name=child.string, codigo=child["value"], facultad=etsetb) #codigo = 'any' + 'num quatri'
        quatri.save()

    return HttpResponse("OK")
    


def loadAssigs(request):
    return HttpResponse("OK")

def cargaAssig(assig):
    return


"""
def loadCarreras(request):    
    
    # Busca els quatris
    ls = parsed.find(attrs={'name':'semester'})
    for child in ls.find_all('option'):
        # print(child["value"],str(child.string))
        quatri = Quatri(name=child.string,codigo=child["value"],facultad=etseib)
        quatri.save()
    # Magic
    return HttpResponse("OK")
""" 
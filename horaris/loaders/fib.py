import requests
import json
from django.http import HttpResponse
from ..models import Carrera, Facultad, Quatri, Asignatura, Grupo

pars = {"client_id": "ZuSzxG72M8rOakSmQhGrD3kMZekVkxYhTM4AOxd9",
        "format": "json", "lang": "ca"}


def loadCarreras(request):
    print("Loading career list... ", end="")
    rq = requests.get("https://api.fib.upc.edu/v2/quadrimestres/", params=pars)
    if not rq.ok:
        return HttpResponse("ERROR QUATRIS")
    quats = json.loads(rq.text)
    rp = requests.get("https://api.fib.upc.edu/v2/plans_estudi/", params=pars)
    if not rp.ok:
        return HttpResponse("ERROR PLANS")
    carrs = json.loads(rp.text)

    print("Clearing fib... ", end="")
    # Si existeix la etseib borrala
    try:
        fib = Facultad.objects.get(name="fib")
        fib.delete()
    except Facultad.DoesNotExist:
        # Si no existeix, no petis
        pass
    fib = Facultad(name="fib")
    fib.save()
    print("creation OK")
    # Afegeix quatris
    for q in quats["results"]:
        print(q["id"])
        qua = Quatri(name=q["id"], codigo=q["id"], facultad=fib)
        qua.save()
    # Afegeix carreres
    for c in carrs["results"]:
        print(c["abreviatura"])
        ca = Carrera(name=c["descripcio"],
                     codigo=c["abreviatura"], facultad=fib)
        ca.save()

    # Magic
    return HttpResponse("OK")


def loadAssigs(request):
    # Carrega la llista d'assignatures per a totes les carreres i quatris de la fib
    try:
        fib = Facultad.objects.get(name="fib")
    except Facultad.DoesNotExist:
        # Si, la has liat una mica parda...
        # potser cridar loadCarreras(request)? <- la HttpResponse petaria...
        # Si l'ordre de crida es fa be, aixó no hauria de passar
        return HttpResponse("ERROR: FIB NOT FOUND")

    cuatris = Quatri.objects.filter(facultad=fib)
    carrs = Carrera.objects.filter(facultad=fib)

    assigsq = {}
    for q in cuatris:
        print("Carregant", q.name, "...")
        rq = requests.get("https://api.fib.upc.edu/v2/quadrimestres/" +
                          q.codigo+"/assignatures/", params=pars)
        if not rq.ok:
            return HttpResponse("ERROR QUATRIS")
        quats = json.loads(rq.text)
        assigsq[q] = quats["results"]
    print("Quatris carregats")
    for c in carrs:
        print("Carregant", c.name, "...")
        rc = requests.get(
            "https://api.fib.upc.edu/v2/assignatures/?pla="+c.codigo, params=pars)
        if not rc.ok:
            return HttpResponse("ERROR PLANS")
        car = json.loads(rc.text)
        for q in assigsq:
            for asi in car["results"]:
                if asi["id"] in assigsq[q]:
                    a = Asignatura(name=asi["nom"], carrera=c, cuatri=q,
                                   codigo=asi["id"], codiUPC=asi["codi_upc"], loaded=False)
                    a.save()
    print("DONE")

    return HttpResponse("OK")


def cargaAssig(assig):
    # Eliminar grupos existentes de la asignatura

    print("Borrant grups...")
    Grupo.objects.filter(assignatura=assig).delete()
    assig.loaded = False
    assig.save()

    q = assig.cuatri
    ra = requests.get("https://api.fib.upc.edu/v2/quadrimestres/" +
                      q.codigo+"/classes/?codi_assig="+assig.codigo, params=pars)
    if not ra.ok:
        return HttpResponse("ERROR GET")
    mods = json.loads(ra.text)
    print("Horaris obtinguts")
    grups = {}
    subg = False
    normg = False
    for mod in mods["results"]:
        if int(mod["grup"]) % 10 == 0:
            normg = True
        else:
            subg = True

        if not mod["grup"] in grups:
            grups[mod["grup"]] = []

        end = mod["inici"].split(":")
        end = str(int(end[0])+mod["durada"])+":"+end[1]

        modul = {
            "start": mod["inici"],
            "end": end,
            "day": mod["dia_setmana"]
        }
        grups[mod["grup"]].append(modul)

    if normg and subg:
        # Cas liat, tenim grups i subgrupos
        print("Cas dificil")
        for grupo in grups:
            gn = int(grupo)
            if gn % 10 != 0:
                g = Grupo(name=str(grupo), assignatura=assig, subgrupo=True,
                          codigo=str(grupo), horario=json.dumps(grups[grupo]+grups[str(gn-(gn % 10))]))
                g.save()
        pass
    else:
        # Cas facil, només grups o subgrups
        print("Cas facil")
        for grupo in grups:
            g = Grupo(name=str(grupo), assignatura=assig, subgrupo=False,
                      codigo=str(grupo), horario=json.dumps(grups[grupo]))
            g.save()

    # Join de grups
    myGroups = Grupo.objects.filter(assignatura=assig)
    for dbGroup in myGroups:

        others = Grupo.objects.filter(assignatura=assig).exclude(pk=dbGroup.pk)
        found = False
        for ng in others:
            if ng.horario == dbGroup.horario:
                found = True
                #print("match!", dbGroup.name, ng.name)
                break
        if found:
            ng.name = ng.name + "/" + dbGroup.name
            #print("newName", ng.name)
            ng.codigo = ng.name
            ng.save()
            dbGroup.delete()

    # Guardamos la asignatura
    assig.loaded = True
    assig.save()

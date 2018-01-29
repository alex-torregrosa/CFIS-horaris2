import requests
import json
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
        carrera = Carrera(name=child.string,
                          codigo=child["value"], facultad=etsetb)
        carrera.save()

    ls = parsed.find(attrs={'name': 'gh_sel_sem'})
    for child in ls.find_all('option'):
        #print(child["value"], str(child.string))
        # codigo = 'any' + 'num quatri'
        quatri = Quatri(name=child.string,
                        codigo=child["value"], facultad=etsetb)
        quatri.save()

    return HttpResponse("OK")


def loadAssigs(request):
    try:
        etsetb = Facultad.objects.get(name="etsetb")
    except Facultad.DoesNotExist:
        return HttpResponse("ERROR: ETSETB NOT FOUND")

    cuatris = Quatri.objects.filter(facultad=etsetb)
    carrs = Carrera.objects.filter(facultad=etsetb)

    for q in cuatris:
        for c in carrs:
            print("Carregant", q.name, " + ", c.name, "...")
            pars = {"_search": "true", "codPla": c.codigo,
                    "curs": q.codigo[:4], "quad": q.codigo[4]}
            rq = requests.get(
                "https://infoteleco.upc.edu/mason-share/docencia/simul_horaris/dades/assig_oferta.mc", params=pars)
            if not rq.ok:
                return HttpResponse("ERROR")
            qc = json.loads(rq.text)
            qcdata = qc["invdata"]  # ?
            for ad in qcdata:
                a = Asignatura(name=ad["nom"], codigo=ad["codi"],
                               codiUPC=ad["codi"], carrera=c, cuatri=q, loaded=False)
                a.save()

            #{"nom":"Radiació i Propagació","curs":"2B","sigles":"RP","codi":"230013"}
    print("DONE")

    return HttpResponse("OK")


def cargaAssig(assig):
    print("Borrant grups...")
    Grupo.objects.filter(assignatura=assig).delete()
    assig.loaded = False
    assig.save()

    pars = {"cod_asig": assig.codigo,
            "semestre": assig.cuatri.codigo[-1], "any": assig.cuatri.codigo[:-1], "cod_pla": assig.carrera.codigo, "_search": "true"}
    # visca els indexs negatius de python
    ra = requests.get(
        "https://infoteleco.upc.edu/mason-share/docencia/simul_horaris/dades/assig_dades.mc", params=pars)
    if not ra.ok:
        return HttpResponse("ERROR GET")
    mods = json.loads(ra.text)
    print("Horaris obtinguts")
    print(ra.url)
    grups = {}
    subg = False
    normg = False
    for g in mods["invdata"][0]["grups"]:
        if g["horaris"] is not None:
            for h in g["horaris"]:
                #{'hora_fin': '19:00:00', 'dia': '5', 'hora_ini': '17:30:00', 'grup': '10'}
                if int(h["grup"]) % 10 == 0:
                    normg = True
                else:
                    subg = True

                if not h["grup"] in grups:
                    grups[h["grup"]] = []

                modul = {
                    "start": h["hora_ini"][:5],
                    "end": h["hora_fin"][:5],
                    "day": int(h["dia"])
                }
                grups[h["grup"]].append(modul)

    if normg and subg:
        for g in grups:
            gn = int(g)
            if gn % 10 != 0:
                gr = Grupo(name=str(g), assignatura=assig, subgrupo=True, codigo=str(
                    g), horario=json.dumps(grups[g]+grups[str(gn-(gn % 10))]))
                gr.save()
    else:
        for g in grups:
            gr = Grupo(name=str(g), assignatura=assig, subgrupo=False,
                       codigo=str(g), horario=json.dumps(grups[g]))
            gr.save()

    myGroups = Grupo.objects.filter(assignatura=assig)
    for dbGroup in myGroups:
        others = Grupo.objects.filter(assignatura=assig).exclude(pk=dbGroup.pk)
        found = False
        for ng in others:
            if ng.horario == dbGroup.horario:
                found = True
                break
        if found:
            ng.name = ng.name + "/" + dbGroup.name
            ng.codigo = ng.name
            ng.save()
            dbGroup.delete()

    assig.loaded = True
    assig.save()

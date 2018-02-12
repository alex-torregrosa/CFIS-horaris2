import json
import requests
import time
from .models import Asignatura, Grupo
from bs4 import BeautifulSoup
from .loaders import etseib, fib, etsetb
import horaris.filters as filters
from .sorter import Sorter
# Aqui se hace la magia de los horarios


def sendProgress(msg, text, progress):
    # Función magica que se comunica con el cliente mediante ligeras vibraciones en la fuerza (a.k.a websockets)
    res = {
        "text": json.dumps({
            "progress": progress,
            "text": text,
            "completed": False
        })
    }
    # Sino triga massa poc i s'omple la cua al treballar amb moltes assignatures
    time.sleep(0.05)
    msg.reply_channel.send(res, immediately=True)


def calculaHorari(data, msg):
    # Funció PRINCIPAL del websocket
    assigs = []
    # Fetch classes
    for el in data["assignatures"]:
        assigs.append(Asignatura.objects.get(pk=data["assignatures"][el]))
    sendProgress(msg, "Asignatures carregades", 10)
    total = len(assigs)
    for x in range(0, total):
        sendProgress(msg, "Carregant horaris per a " +
                     assigs[x].name, 10 + (x / total) * 20)
        if not assigs[x].loaded:
            print("Carregant horari de",  assigs[x].name)
            if assigs[x].carrera.facultad.name == "etseib":
                etseib.cargaAssig(assigs[x])
            elif assigs[x].carrera.facultad.name == "fib":
                fib.cargaAssig(assigs[x])
            elif assigs[x].carrera.facultad.name == "etsetb":
                etsetb.cargaAssig(assigs[x])

    sendProgress(msg, "Generant horaris...", 30)
    # Ara toca obtenir tots els grups
    groups = []
    for i in range(0, total):
        groups.append(Grupo.objects.filter(assignatura=assigs[i]))
    # Generem els horaris
    horaris = genHoraris(groups, data["filters"])

    sendProgress(msg, str(len(horaris)) +
                 " horaris possibles, ordenant...", 40)

    s = Sorter()
    s.set_fi_p(10)

    horaris.sort(key=s.puntua, reverse=True)

    sendProgress(msg, "Descarregant...", 90)
    if len(horaris) > 0:
        exphor = []
        # Només exportem els 100 primers horaris
        for x in range(0, min(100, len(horaris))):
            exphor.append(exporta(horaris[x]))
        res = {
            "text": json.dumps({
                "horaris": exphor,
                "completed": True
            })
        }
        msg.reply_channel.send(res, immediately=True)
    else:
        sendProgress(msg, "Cap horari trobat", 100)


def genHoraris(grups, filtres):
    # Genera els horaris a partir de grups (recursivament)
    if len(grups) == 0:
        return []
    g = grups[0]
    # Generem els horaris de tots els grups menys el primer
    horig = genHoraris(grups[1:], filtres)
    horaris = []
    if horig == []:
        for grup in g:
            hor = [grup]
            horaris.append(hor)
    else:
        for grup in g:
            for h in horig:
                if not filters.solapament(h, grup):  # Filtre de solapaments
                    horaris.append(h + [grup])
    # del horig
    # print(len(horaris), len(grups), g[0]) #peta si la query no retorna res (g[0] = QuerySet [])
    return horaris


def exporta(horari):
    res = []
    baset = time.time()
    baset -= time.localtime(baset).tm_wday * 3600 * 24
    colors = ["#d50000", "#304ffe", "#00c853", "#ffd600", "#aa00ff",
              "#0091ea", "#ff6d00", "#263238", "#ff6d00", "10", "11", "12"]
    act = 0
    for g in horari:
        h = json.loads(g.horario)
        n = g.assignatura.name
        ng = g.name
        for c in h:
            mt = time.localtime(baset + (c["day"] - 1) * 24 * 3600)
            st = time.strftime("%Y-%m-%dT", mt)
            ev = {}
            ev["title"] = n + " (" + ng + ")"
            ev["start"] = st + c["start"]
            ev["end"] = st + c["end"]
            ev["color"] = colors[act]
            res.append(ev)
        act += 1
    return res

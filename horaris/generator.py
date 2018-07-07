""" Generador de horaris"""
import json
import time
from horaris import filters
from .models import Asignatura, Grupo
from .loaders import etseib, fib, etsetb
from .sorter import Sorter
# Aqui se hace la magia de los horarios


def send_progress(consum, text, progress):
    """ Función magica que se comunica con el cliente mediante ligeras vibraciones
    en la fuerza (a.k.a websockets)"""
    res = {
        "progress": progress,
        "text": text,
        "completed": False
    }
    print("[WS] ", text)
    consum.send_json(res)


def calcula_horari(data, consumer):
    """Funció PRINCIPAL del websocket"""
    assigs = []
    # Fetch classes
    for el in data["assignatures"]:
        assigs.append(Asignatura.objects.get(pk=data["assignatures"][el]))
    send_progress(consumer, "Asignatures carregades", 10)
    total = len(assigs)
    for x in range(0, total):
        send_progress(consumer, "Carregant horaris per a " +
                      assigs[x].name, 10 + (x / total) * 20)
        if not assigs[x].loaded:
            print("Carregant horari de", assigs[x].name)
            if assigs[x].carrera.facultad.name == "etseib":
                etseib.cargaAssig(assigs[x])
            elif assigs[x].carrera.facultad.name == "fib":
                fib.cargaAssig(assigs[x])
            elif assigs[x].carrera.facultad.name == "etsetb":
                etsetb.cargaAssig(assigs[x])

    send_progress(consumer, "Generant horaris...", 30)
    # Ara toca obtenir tots els grups
    groups = []
    for i in range(0, total):
        groups.append(Grupo.objects.filter(assignatura=assigs[i]))
    # Generem els horaris
    horaris = genHoraris(groups, data["filters"])

    send_progress(consumer, str(len(horaris)) +
                  " horaris possibles, ordenant...", 40)

    s = Sorter()
    s.set_fi_p(10)

    horaris.sort(key=s.puntua, reverse=True)
    for elemento1 in horaris[:5]:
        print(elemento1, s.puntua(elemento1))
    send_progress(consumer, "Descarregant...", 90)
    if horaris:
        exphor = []
        # Només exportem els 100 primers horaris
        for x in range(0, min(100, len(horaris))):
            exphor.append(exporta(horaris[x]))
        res = {
            "horaris": exphor,
            "completed": True
        }

        consumer.send_json(res)
    else:
        send_progress(consumer, "Cap horari trobat", 100)


def genHoraris(grups, filtres):
    # Genera els horaris a partir de grups (recursivament)
    if not grups:
        return []
    old_g = grups[0]
    g = []
    # Filtra els grups
    for grup in old_g:
        filtrat = True
        if filtres["list"]["inici"]:
            filtrat = not filters.inici(grup, filtres["data"]["inici"])
        if filtrat and filtres["list"]["fi"]:
            filtrat = not filters.fi(grup, filtres["data"]["fi"])
        if filtrat:
            g.append(grup)
    if not g:
        return []

        # Generem els horaris de tots els grups menys el primer [BACKTRACKING]
    horig = genHoraris(grups[1:], filtres)
    horaris = []
    if horig == [] and not grups[1:]:
        for grup in g:
            hor = [grup]
            horaris.append(hor)
    else:
        for grup in g:
            for h in horig:
                # Filtre obligatori de solapaments
                filtrat = not filters.solapament(h, grup)

                if filtrat:
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

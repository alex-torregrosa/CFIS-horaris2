import json
from .models import Asignatura, Grupo
from time import sleep
import requests
from bs4 import BeautifulSoup

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

    msg.reply_channel.send(res, immediately=True)


def calculaHorari(asignaturas, msg):
    # Funció PRINCIPAL del websocket
    assigs = []
    # Fetch classes
    for el in asignaturas:
        assigs.append(Asignatura.objects.get(pk=asignaturas[el]))
    sendProgress(msg, "Asignaturas cargadas", 10)
    total = len(assigs)
    for x in range(0, total):
        sendProgress(msg, "Cargando horarios para " +
                     assigs[x].name, 10 + (x / total) * 20)
        if not assigs[x].loaded:
            # TODO: mes facus
            cargaAssigETSEIB(assigs[x])

    sendProgress(msg, "Horarios cargados", 30)
    # Ara toca obtenir tots els grups
    groups = []
    for i in range(0, total):
        groups.append(Grupo.objects.filter(assignatura=assigs[i]))

    horaris = genHoraris(groups)
    sendProgress(msg, str(len(horaris)) + " horarios posibles", 40)
    print(horaris[0])


def genHoraris(grups):
    # Genera els horaris a partir de grups (recursivament)
    if len(grups) == 0:
        return []
    g = grups[0]
    # Generem els horaris de tots els grups menys el primera
    horig = genHoraris(grups[1:])
    horaris = []
    if horig == []:
        for grup in g:
            hor = [grup]
            horaris.append(hor)
    else:
        for grup in g:
            for h in horig:
                hor = h + [grup]
                horaris.append(hor)
    return horaris


def cargaAssigETSEIB(assig):
    # Eliminar grupos existentes de la asignatura
    Grupo.objects.filter(assignatura=assig).delete()
    assig.loaded = False
    assig.save()
    # Cargar lista de grupos
    deg = assig.carrera
    q = assig.cuatri
    r = requests.get("https://guiadocent.etseib.upc.edu/simgen/form/simulator.php?lang=es&degree=" +
                     str(deg.codigo) + "&semester=" + q.codigo + "&" + assig.codigo)
    parsed = BeautifulSoup(r.text, "html.parser")
    grups = parsed.find_all(attrs={'type': 'checkbox'})
    subgrupos = False
    grupos = {}
    # Loop de grupos
    for child in grups:
        grupid = child["name"]
        if grupid != "autoRefresh":
            grupnum = int(grupid.split("_")[2])
            # Cargar horario del grupo
            horari = getHorariETSEIB(str(deg.codigo), q.codigo, grupid)
            grupos[grupnum] = {"id": grupid, "horari": horari}
            # Detector de subgrupos
            if grupnum % 10 != 0:
                subgrupos = True
    print("Downloaded")
    # Postprocesado
    if(subgrupos):
        for grupo in grupos:
            if grupo % 10 != 0:
                b10 = grupo - grupo % 10
                print(grupo, b10)

                if b10 in grupos:  # Podría no haber grupos...
                    grupos[grupo]["horari"] += grupos[b10]["horari"]
                # Creamos finalmente el grupo
                g = Grupo(name=str(grupo), assignatura=assig, subgrupo=True,
                          codigo=grupos[grupo]["id"], horario=json.dumps(grupos[grupo]["horari"]))
                g.save()

    else:
        for grupo in grupos:
            # No hay subgrupos, a saco
            print(grupo)
            g = Grupo(name=str(grupo), assignatura=assig, subgrupo=False,
                      codigo=grupos[grupo]["id"], horario=json.dumps(grupos[grupo]["horari"]))
            g.save()
    # Guardamos la asignatura
    assig.loaded = True
    assig.save()


def getHorariETSEIB(grau, quatri, grup):
    # Descargamos la tabla del horario
    r = requests.get("https://guiadocent.etseib.upc.edu/simgen/action/result.php?lang=es&degree=" +
                     grau + "&semester=" + quatri + "&" + grup)
    parsed = BeautifulSoup(r.text, "html.parser")
    # Buscamos los bloques del color correcto
    moduls = parsed.find_all(attrs={"bgcolor": "#F6CECE", "valign": "top"})
    # print(moduls)
    horari = []
    for el in moduls:
        # El th que dice la hora
        h = el.parent.parent.parent.parent.find("th").string
        # Numero de casillas antes
        sibs = el.parent.parent.parent.previous_siblings
        size = 0
        # Em sona que no es podia utilitzar un .size(), VALE, no em jutgis... (Si ho fas, WA abans que EE)
        for e in sibs:
            size += 1
        [start, end] = h.split("-")
        # I així queda definida la increible estructura de dades que utilitzarem per a guardar horaris
        modul = {
            "start": start,
            "end": end,
            "day": size
        }
        horari.append(modul)

    # TODO: Filtrar els moduls per juntar els adjacents

    return horari

import json
from .models import Asignatura, Grupo
from time import sleep
import requests
from bs4 import BeautifulSoup
from .loaders import etseib, fib
import horaris.filters as filters

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
    sleep(0.1) #ELIMINAR!!!
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
            print("FORCE LOAD")
            if assigs[x].carrera.facultad.name == "etseib":
                etseib.cargaAssig(assigs[x])
            elif assigs[x].carrera.facultad.name == "fib":
                fib.cargaAssig(assigs[x])

    sendProgress(msg, "Horarios cargados", 30)
    # Ara toca obtenir tots els grups
    groups = []
    for i in range(0, total):
        groups.append(Grupo.objects.filter(assignatura=assigs[i]))

    horaris = genHoraris(groups)
    sendProgress(msg, str(len(horaris)) + " horarios posibles", 40)
    # print(horaris[0])


def genHoraris(grups):
    # Genera els horaris a partir de grups (recursivament)
    if len(grups) == 0:
        return []
    g = grups[0]
    # Generem els horaris de tots els grups menys el primer
    horig = genHoraris(grups[1:])
    horaris = []
    if horig == []:
        for grup in g:
            hor = [grup]
            horaris.append(hor)
    else:
        for grup in g:
            for h in horig:
                if not filters.solapament(h,grup): #Filtre de solapaments
                    horaris.append(h + [grup])
    # del horig
    print(len(horaris), len(grups), g[0])
    return horaris

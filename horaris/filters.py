from .models import Grupo
import json

# Horari: array de grups
# grup: veure models.py
# grup.horario: array de classes
# classe: dict amb start, end i day
#


def solapament(horari, grup):
    # Indica si a un horari hi ha solapaments
    hor = json.loads(grup.horario)
    for g in horari:
        hor2 = json.loads(g.horario)
        for classe1 in hor:
            for classe2 in hor2:
                if solapen(classe1, classe2):
                    return True
    return False


def inici(grup, hora):
    # Indica si un grup te classes abans de l'hora donada
    hor = json.loads(grup.horario)
    for classe in hor:
        if classe["start"] < hora:
            return True
    return False


def fi(grup, hora):
    # Indica si un grup te classes despres de l'hora donada
    hor = json.loads(grup.horario)
    for classe in hor:
        if classe["end"] > hora:
            return True
    return False


def solapen(c1, c2):
    # Indica si dues classes es solapen

    # Dia diferent
    if c1["day"] != c2["day"]:
        return False

    # Fix per als labs random d'indus. (es pot solapar amb teoria, no labs)
    # TODO: fer-ho opcional
    if c1["type"] == 2 and c2["type"] == 0:
        return False
    if c2["type"] == 2 and c1["type"] == 0:
        return False

    # Inici o final iguals
    if c1["start"] == c2["start"] or c1["end"] == c2["end"]:
        return True
    # Solapaments i tal
    if c1["start"] > c2["start"]:
        if c1["start"] < c2["end"]:
            return True
        else:
            return False
    else:  # c1start < c2start
        if c2["start"] < c1["end"]:
            return True
        else:
            return False

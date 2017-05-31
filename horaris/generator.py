import json
from .models import Asignatura, Grupo
from time import sleep
import requests
from bs4 import BeautifulSoup

def sendProgress(msg, text, progress):
    res = {
        "text": json.dumps({
            "progress": progress,
            "text":text,
            "completed": False
        })
    }

    msg.reply_channel.send(res,immediately=True)


def calculaHorari(asignaturas, msg):
    assigs = []
    # Fetch classes
    for el in asignaturas:
        assigs.append(Asignatura.objects.get(pk=asignaturas[el]))
    sendProgress(msg,"Asignaturas cargadas", 10)
    total = len(assigs)
    for x in range(0,total):
        sendProgress(msg,"Cargando horarios para " +assigs[x].name, 10 + (x/total)*20)
        if not assigs[x].loaded:
            cargaAssigETSEIB(assigs[x])

    sendProgress(msg,"Horarios cargados", 30)


def cargaAssigETSEIB(assig):
    Grupo.objects.filter(assignatura=assig).delete()
    assig.loaded=False
    assig.save()
    deg = assig.carrera
    q = assig.cuatri
    r = requests.get("https://guiadocent.etseib.upc.edu/simgen/form/simulator.php?lang=es&degree="+str(deg.codigo)+"&semester="+q.codigo+"&"+assig.codigo)
    parsed = BeautifulSoup(r.text,"html.parser")
    grups = parsed.find_all(attrs={'type':'checkbox'})
    subgrupos = False;
    grupos = {}
    for child in grups:
        grupid = child["name"]
        if grupid != "autoRefresh":
            grupnum = int(grupid.split("_")[2])
            horari=getHorariETSEIB(str(deg.codigo),q.codigo,grupid)
            grupos[grupnum] = {"id":grupid,"horari":horari}
            if grupnum % 10 != 0:
                subgrupos = True
    print("Downloaded")
    if(subgrupos):
        for grupo in grupos:
            if grupo%10 != 0:
                b10 = grupo -grupo%10
                print(grupo,b10)
                grupos[grupo]["horari"] += grupos[b10]["horari"]
                g = Grupo(name=str(grupo),assignatura=assig,subgrupo=True,codigo=grupos[grupo]["id"],horario=json.dumps(grupos[grupo]["horari"]))
                g.save()

    else:
        for grupo in grupos:
            print(grupo)
            g = Grupo(name=str(grupo),assignatura=assig,subgrupo=False,codigo=grupos[grupo]["id"],horario=json.dumps(grupos[grupo]["horari"]))
            g.save()

    assig.loaded=True
    assig.save()



def getHorariETSEIB(grau,quatri,grup):
    r = requests.get("https://guiadocent.etseib.upc.edu/simgen/action/result.php?lang=es&degree="+grau+"&semester="+quatri+"&"+grup)
    parsed = BeautifulSoup(r.text,"html.parser")
    moduls = parsed.find_all(attrs={"bgcolor":"#F6CECE","valign":"top"})
    # print(moduls)
    horari = []
    for el in moduls:
        h = el.parent.parent.parent.parent.find("th").string
        sibs = el.parent.parent.parent.previous_siblings
        size = 0;
        for e in sibs:
            size += 1
        [start,end] = h.split("-")
        modul={
            "start":start,
            "end": end,
            "day":size
        }
        horari.append(modul)

    return horari

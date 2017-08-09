import requests, json
from bs4 import BeautifulSoup
from django.http import HttpResponse
from ..models import Carrera, Facultad, Quatri, Asignatura, Grupo

def loadCarreras(request):
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
        carrera = Carrera(name=child.string,codigo=child["value"],facultad=etseib)
        carrera.save()
    # Busca els quatris
    ls = parsed.find(attrs={'name':'semester'})
    for child in ls.find_all('option'):
        # print(child["value"],str(child.string))
        quatri = Quatri(name=child.string,codigo=child["value"],facultad=etseib)
        quatri.save()
    # Magic
    return HttpResponse("OK")

def loadAssigs(request):

    # Carrega la llista d'assignatures per a totes les carreres i quatris de la etseib
    # TODO: Molaria ficar-la a un CRON o similar
    try:
        etseib = Facultad.objects.get(name="etseib")
    except Facultad.DoesNotExist:
        #Si, la has liat una mica parda...
        # potser cridar loadCarreras(request)? <- la HttpResponse petaria...
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

def cargaAssig(assig):
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
            horari = getHorari(str(deg.codigo), q.codigo, grupid)
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
                    for el in grupos[b10]["horari"]:
                        if el not in grupos[grupo]["horari"]:
                            grupos[grupo]["horari"].append(el)
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


def getHorari(grau, quatri, grup):
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
        #ModuleMerger
        added = False
        for mod in horari:
            if mod["day"] == modul["day"]:
                # print(mod["start"], modul["start"], mod["start"] == modul["start"])
                if mod["start"] == modul["start"]:
                    added = True
                    if modul["end"]>mod["end"]:
                        mod["end"] = modul["end"]

                    break
                if mod["end"] == modul["start"]:
                    mod["end"] = modul["end"]
                    added = True
                    break
        if not added:
            horari.append(modul)



    return horari

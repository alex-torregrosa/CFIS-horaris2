import json


class Sorter:
    # Classe per a ordenar horaris
    def __init__(self):
        self.fi_p = 0
        self.inici_p = 0

    # Configuradores
    def set_fi_p(self, n):
        self.fi_p = n

    def set_inici_p(self, n):
        self.inici_p = n

    def puntua(self, horari):
        # Dona una puntuació a cada horari a partir de les prioritats donades
        punts = 0
        if self.fi_p > 0:
            punts += self.hora_fi(horari) * self.fi_p
        if self.inici_p > 0:
            punts += self.hora_inici(horari) * self.inici_p
        return punts

    # Funcions de puntuació, retornen un valor entre 0 i 100
    def hora_fi(self, horari):
        horaf = "00:00"
        for g in horari:
            h = json.loads(g.horario)
            for c in h:
                if c["end"] > horaf:
                    horaf = c["end"]
        h = horaf.split(":")
        h = int(h[0]) + (int(h[1]) / 60) - 8
        h = 13 - h
        return h * 100 / 13

    def hora_inici(self, horari):
        horari = "24:00"
        for g in horari:
            h = json.loads(g.horario)
            for c in h:
                if c["start"] < horai:
                    horai = c["start"]
        h = horai.split(":")
        h = int(h[0]) + (int(h[1]) / 60) - 8

        return h * 100 / 13

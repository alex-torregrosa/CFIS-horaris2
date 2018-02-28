""" Funcions de comparació d'horaris"""
import json


class Sorter:
    """Classe per a ordenar horaris"""

    def __init__(self):
        self.fi_p = 0
        self.inici_p = 0

    # Configuradores
    def set_fi_p(self, weight):
        """ Ajusta el pes de l'hora de finalització"""
        self.fi_p = weight

    def set_inici_p(self, weight):
        """ Ajusta el pes de l'hora d'inici"""
        self.inici_p = weight

    def puntua(self, horari):
        """Dona una puntuació a cada horari a partir de les prioritats donades"""
        punts = 0
        if self.fi_p > 0:
            punts += self.hora_fi(horari) * self.fi_p
        if self.inici_p > 0:
            punts += self.hora_inici(horari) * self.inici_p
        return punts

    # Funcions de puntuació, retornen un valor entre 0 i 100
    def hora_fi(self, horari):
        """Puntua un horari amb una nota entre 0 i 100 en funció de la seva hora
        de finalització"""
        horaf = "00:00"
        for grup in horari:
            horari_grup = json.loads(grup.horario)
            for classe in horari_grup:
                if classe["end"] > horaf:
                    horaf = classe["end"]
        hora = horaf.split(":")
        hora = int(hora[0]) + (int(hora[1]) / 60) - 8
        hora = 13 - hora
        return hora * 100 / 13

    def hora_inici(self, horari):
        """Puntua un horari amb una nota entre 0 i 100 en funció de
        la seva hora d'inici"""
        horai = "24:00"
        for grup in horari:
            horari_grup = json.loads(grup.horario)
            for classe in horari_grup:
                if classe["start"] < horai:
                    horai = classe["start"]
        hora = horai.split(":")
        hora = int(hora[0]) + (int(hora[1]) / 60) - 8

        return hora * 100 / 13

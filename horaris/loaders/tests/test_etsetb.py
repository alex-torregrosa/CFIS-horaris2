from django.test import TestCase, RequestFactory
from django.urls import reverse
from horaris.loaders import etsetb
from horaris.models import Asignatura, Grupo, Facultad, Quatri, Carrera
from random import randint


class TestsEtsetb(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def create(self):
        """ETSETB loads correctly"""
        request = self.factory.get(reverse("etsetbInit"))
        response = etsetb.loadCarreras(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")
        facu = Facultad.objects.get(name="etsetb")
        self.assertGreater(len(Quatri.objects.filter(facultad=facu)), 0)
        self.assertGreater(len(Carrera.objects.filter(facultad=facu)), 0)

    def load(self):
        """ETSETB loads subject list correctly"""
        request = self.factory.get(reverse("etsetbAssigs"))
        response = etsetb.loadAssigs(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")
        # Check it actually loaded something
        facu = Facultad.objects.get(name="etsetb")
        Q = Quatri.objects.filter(facultad=facu)[0]
        self.assertGreater(len(Asignatura.objects.filter(cuatri=Q)), 0)

    def test_etsetb(self):
        """Test all the faculty"""
        self.create()
        self.load()
        facu = Facultad.objects.get(name="etsetb")
        quatri = Quatri.objects.filter(facultad=facu)[0]
        assig = Asignatura.objects.filter(cuatri=quatri)
        assig = assig[randint(0, len(assig))]
        grup = Grupo.objects.filter(assignatura=assig)
        self.assertEqual(len(grup), 0)
        etsetb.cargaAssig(assig)
        grup = Grupo.objects.filter(assignatura=assig)
        self.assertGreater(len(grup), 0)

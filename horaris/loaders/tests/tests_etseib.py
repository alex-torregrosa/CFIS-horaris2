from django.test import TestCase, RequestFactory
from django.urls import reverse
from horaris.loaders import etseib
from horaris.models import Asignatura, Grupo, Facultad, Quatri, Carrera


class TestsEtseib(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_etseib_not_exists(self):
        """ Test loading fail when init has not runned yet"""
        request = self.factory.get(reverse("etseibAssigs"))
        response = etseib.loadAssigs(request)
        self.assertEqual(response.status_code, 200)
        print("RESPONSE:", response)
        self.assertContains(response, "ERROR")

    def create(self):
        """ETSEIB loads correctly"""
        request = self.factory.get(reverse("etseibInit"))
        response = etseib.loadCarreras(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")
        facu = Facultad.objects.get(name="etseib")
        self.assertGreater(len(Quatri.objects.filter(facultad=facu)), 0)
        self.assertGreater(len(Carrera.objects.filter(facultad=facu)), 0)

    def load(self):
        """ETSEIB loads subject list correctly"""
        request = self.factory.get(reverse("etseibAssigs"))
        response = etseib.loadAssigs(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")
        # Check it actually loaded something
        facu = Facultad.objects.get(name="etseib")
        Q = Quatri.objects.filter(facultad=facu)[0]
        self.assertGreater(len(Asignatura.objects.filter(cuatri=Q)), 0)

    def test_etseib(self):
        """Test all the faculty"""
        self.create()
        self.load()

        # assignatura amb subgrups (Dinàmica de sistemes)
        assig = Asignatura.objects.filter(codiUPC="240043")[0]
        grup = Grupo.objects.filter(assignatura=assig)
        self.assertEqual(len(grup), 0)
        etseib.cargaAssig(assig)
        grup = Grupo.objects.filter(assignatura=assig)
        self.assertGreater(len(grup), 0)

        # assignatura sense subgrups (Mecànica)
        assig = Asignatura.objects.filter(codiUPC="240133")[0]
        grup = Grupo.objects.filter(assignatura=assig)
        self.assertEqual(len(grup), 0)
        etseib.cargaAssig(assig)
        grup = Grupo.objects.filter(assignatura=assig)
        self.assertGreater(len(grup), 0)

        # assignatura amb labs random (Electromagnetisme)
        assig = Asignatura.objects.filter(codiUPC="240031")[0]
        grup = Grupo.objects.filter(assignatura=assig)
        self.assertEqual(len(grup), 0)
        etseib.cargaAssig(assig)
        grup = Grupo.objects.filter(assignatura=assig)
        self.assertGreater(len(grup), 0)

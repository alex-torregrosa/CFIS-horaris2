from django.test import TestCase
from .loaders import etseib, fib, etsetb
from django.urls import reverse
from .models import Asignatura, Grupo, Facultad


def createFacultats():
    Facultad(name="etseib").save()
    Facultad(name="fib").save()
    Facultad(name="etsetb").save()


class HorarisTests(TestCase):

    def test_main_page_load(self):
        """Main page loads correctly"""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_js_load(self):
        """Javascript loads"""
        r = self.client.get(reverse("mainjs"))
        self.assertEqual(r.status_code, 200)
        # verify that acually was my js code
        self.assertContains(r, "$(document).ready(function ()")

    def test_facultad_creation(self):
        createFacultats()

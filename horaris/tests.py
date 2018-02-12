from django.test import TestCase
from .loaders import etseib, fib, etsetb
from django.urls import reverse


# Create your tests here.
class HorarisTests(TestCase):
    def test_etseib_creation(self):
        """Etseib loads correctly"""
        response = self.client.get(reverse("etseibInit"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")

    def test_fib_creation(self):
        """FIB loads correctly"""
        response = self.client.get(reverse("fibInit"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")

    def test_etsetb_creation(self):
        """Etsetb loads correctly"""
        response = self.client.get(reverse("etsetbInit"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OK")

    def test_main_page_load(self):
        """Main page loads correctly"""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

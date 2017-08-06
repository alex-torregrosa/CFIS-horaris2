from django.db import models

# Create your models here.


class Facultad(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Carrera(models.Model):
    name = models.CharField(max_length=200)
    facultad = models.ForeignKey(
        Facultad, on_delete=models.CASCADE, default=None)
    codigo = models.IntegerField()

    def __str__(self):
        return self.name


class Quatri(models.Model):
    name = models.CharField(max_length=200)
    codigo = models.CharField(max_length=200)
    facultad = models.ForeignKey(
        Facultad, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.name


class Asignatura(models.Model):
    name = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    codiUPC = models.CharField(max_length=50)
    carrera = models.ForeignKey(
        Carrera, on_delete=models.CASCADE, default=None)
    cuatri = models.ForeignKey(Quatri, on_delete=models.CASCADE, default=None)
    loaded = models.BooleanField(default=False)
    lastLoadTime = models.DateField(auto_now=True)

    def __str__(self):
        return self.name + " [" + str(self.codiUPC) + "]"


class Grupo(models.Model):
    codigo = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    horario = models.CharField(max_length=900)
    assignatura = models.ForeignKey(
        Asignatura, on_delete=models.CASCADE, default=None)
    subgrupo = models.BooleanField()

    def __str__(self):
        return self.name + " (" + self.assignatura.name + ")"

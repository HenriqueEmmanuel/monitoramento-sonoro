from django.db import models

class NiveisDeRuido(models.Model):
    data = models.CharField(max_length=10)
    hora = models.CharField(max_length=8)
    decibeis = models.FloatField()
    limite = models.FloatField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.data} {self.hora} - {self.status}"

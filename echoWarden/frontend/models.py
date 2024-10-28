from django.db import models

# Create your models here.


class Usuario(models.Model):
    nome = models.TextField(max_length=60)
    email = models.TextField(max_length=60)
    password = models.TextField(max_length=200)
from django.db import models

class NiveisDeRuido(models.Model):
    data = models.DateField(null=False, blank=False)
    hora = models.TimeField()  
    decibeis = models.FloatField()
    limite = models.FloatField()
    status = models.BooleanField()  
    
    

    class Meta:
        indexes = [
            models.Index(fields=['data', 'hora']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.data} {self.hora.strftime('%H:%M:%S')} - {'Perturbado' if self.status else 'Normal'}"



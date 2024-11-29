from django.db import models

class NiveisDeRuido(models.Model):
    data = models.DateField(null=False, blank=False)
    hora = models.TimeField()  # Hora como TimeField
    decibeis = models.FloatField()
    limite = models.FloatField()
    status = models.BooleanField()  # Status como BooleanField (True/False)
    
    # Meta para melhorar a performance nas buscas (índices)
    class Meta:
        indexes = [
            models.Index(fields=['data', 'hora']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        # Exibe uma string mais informativa com a data, hora e status
        return f"{self.data} {self.hora.strftime('%H:%M:%S')} - {'Perturbado' if self.status else 'Normal'}"

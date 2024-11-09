from rest_framework import serializers
from .models import NiveisDeRuido

class NiveisDeRuidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NiveisDeRuido
        fields = '__all__'

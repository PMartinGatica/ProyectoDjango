from rest_framework import serializers
from .models import MQS, MES, Pendiente, YieldTurno, Sampling

class MQSSerializer(serializers.ModelSerializer):
    class Meta:
        model = MQS
        fields = '__all__'

class MESSerializer(serializers.ModelSerializer):
    class Meta:
        model = MES
        fields = '__all__'

class PendienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pendiente
        fields = '__all__'

class YieldTurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = YieldTurno
        fields = '__all__'

class SamplingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sampling
        fields = '__all__'

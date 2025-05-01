from django.shortcuts import render
from rest_framework import viewsets
from .models import MQS, MES, Pendiente, YieldTurno, Sampling
from .serializers import (
    MQSSerializer, MESSerializer, PendienteSerializer,
    YieldTurnoSerializer, SamplingSerializer
)

class MQSViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MQS.objects.all()
    serializer_class = MQSSerializer

class MESViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MES.objects.all()
    serializer_class = MESSerializer

class PendienteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pendiente.objects.all()
    serializer_class = PendienteSerializer

class YieldTurnoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = YieldTurno.objects.all()
    serializer_class = YieldTurnoSerializer

class SamplingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sampling.objects.all()
    serializer_class = SamplingSerializer

from rest_framework import serializers, viewsets, routers
from .models import MQS, MES, Pendiente, YieldTurno, Sampling

# 1) Serializers
class MQSSerializer(serializers.ModelSerializer):
    class Meta:
        model = MQS
        fields = '__all__'

# (repetir para MES, Pendiente, YieldTurno, Sampling)

# 2) ViewSets
class MQSViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MQS.objects.all().order_by('-Date','-Time')
    serializer_class = MQSSerializer

# (repetir para cada modelo)

# 3) Router
router = routers.DefaultRouter()
router.register(r'mqs', MQSViewSet)
# router.register(r'mes', MESViewSet) etc…

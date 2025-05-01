# load_sampling.py
from datetime import date, time
import django, os

os.environ.setdefault('DJANGO_SETTINGS_MODULE','Proyecto1.settings')
django.setup()

from quality.models import Sampling

# 5 registros CQA
for i in range(5):
    Sampling.objects.create(tipo='CQA', Fecha=date.today(), Hora=time(12,0), dato=f'data_cqa_{i}')

# 5 registros OQC
for i in range(5):
    Sampling.objects.create(tipo='OQC', Fecha=date.today(), Hora=time(13,0), dato=f'data_oqc_{i}')

print("✅ 10 filas Sampling insertadas")

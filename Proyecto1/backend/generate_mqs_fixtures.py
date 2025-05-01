# backend/generate_mqs_fixtures.py
import pandas as pd
import json
from pathlib import Path

# ------------------------------------------------------------------
# 1) Ruta al CSV (ajústala si lo has movido)
# ------------------------------------------------------------------
csv_path = Path(__file__).parent / 'Copia de MQS 0.94 - 14dias.csv'
df = pd.read_csv(csv_path, dtype=str)

# ------------------------------------------------------------------
# 2) Construcción de la lista de fixtures
# ------------------------------------------------------------------
fixtures = []
for _, row in df.iterrows():
    # Convertimos a string y luego strip/upper para protegernos de floats/NaN
    ntf_flag   = str(row.get('NTF?', '')).strip().upper()   == 'Y'
    prime_flag = str(row.get('Prime?', '')).strip().upper() == 'Y'

    fixture = {
        "model": "quality.mqs",
        "pk": int(row['ID']),
        "fields": {
            "Date": row['Date'],        # YYYY-MM-DD
            "Time": row['Time'],        # HH:MM:SS
            "Line": row['Line'],
            "Family": row['Family'],
            "Model": row['Model'],
            "Process": row['Process'],
            "Station": row['Station'],
            "Fixture": row['Fixture'],
            "TrackId": row['TrackId'],
            "NTF": ntf_flag,
            "Prime": prime_flag,
            "Testcode": row['Testcode'],
            "Testcode_Desc": row['Testcode Desc'],
            "Fail_Desc": row['Fail Desc'],
            "TestTime": float(row['TestTime']),
            "Test_Val": float(row['Test Val']),
            "LL": float(row['LL']),
            "UL": float(row['UL'])
        }
    }
    fixtures.append(fixture)

# ------------------------------------------------------------------
# 3) Guardar JSON en quality/fixtures/mqs.json
# ------------------------------------------------------------------
out_dir = Path(__file__).parent / 'quality' / 'fixtures'
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / 'mqs.json'

with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(fixtures, f, indent=2, ensure_ascii=False)

print(f"✅ Se han generado {len(fixtures)} objetos en {out_file}")

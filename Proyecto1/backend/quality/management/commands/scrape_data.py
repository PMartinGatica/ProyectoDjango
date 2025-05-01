from pathlib import Path
import sys

# Inserta la carpeta raíz (donde está manage.py) en el path de módulos
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


import os, io, time, warnings
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException

from quality.models import MQS, MES, Pendiente, YieldTurno, Sampling

# importa tu entorno2 para Firefox
from App.entorno2 import firefox_service, firefox_option, cargar_configuraciones, config_file_path, download_folder, tmp_directory

# scritps
from scripts import MQS as mod_MQS
from scripts import MES as mod_MES
from scripts import Pendientes as mod_PEND
from scripts import YieldTurno as mod_YT
from scripts import Sampling_hoy as mod_SH
from scripts import Sampling_CQA as mod_SCQA
from scripts import Sampling_OQC as mod_SOQC

# entorno Selenium
from App.entorno2 import firefox_service, firefox_option, cargar_configuraciones, config_file_path, download_folder

class Command(BaseCommand):
    help = "Ejecuta todos los scrapers y guarda en la BBDD via ORM"

    def handle(self, *args, **options):
        browser = webdriver.Firefox(service=firefox_service, options=firefox_option)
        cfg = cargar_configuraciones(config_file_path)

        try:
            # --- MQS ---
            df = mod_MQS.paretoMQS(mod_MQS.ultimos, mod_MQS.hasta)
            for r in df.itertuples(index=False):
                MQS.objects.create(
                    Date=r.Date, Time=r.Time, Line=r.Line, Family=r.Family,
                    Model=r.Model, Process=r.Process, Station=r.Station,
                    Fixture=r.Fixture, TrackId=r._10, NTF=r._11, Prime=r._12,
                    Testcode=r._13, Testcode_Desc=r._14, Fail_Desc=r._15,
                    TestTime=r._16, Test_Val=r._17, LL=r._18, UL=r._19
                )

            # --- MES ---
            mod_MES.consulta_MES()
            new = download_folder / mod_MES.file
            mod_MES.process_MES(new)
            df2 = mod_MES.pd.read_excel(new, header=1).iloc[1:]
            for r in df2.itertuples(index=False):
                MES.objects.create(
                    FECHA_REPARACION=r.FECHA_REPARACION, HORA_REPARACION=r.HORA_REPARACION,
                    FECHA_RECHAZO=r.FECHA_RECHAZO, HORA_RECHAZO=r.HORA_RECHAZO,
                    POSICION=r.POSICION, FUNCION=r.FUNCION, CODIGO_FALLA=r.CODIGO_DE_FALLA_REPARACION,
                    CAUSA=r.CAUSA_DE_REPARACION, ACCION=r.ACCION_CORRECTIVA,
                    ORIGEN=r.ORIGEN, IMAGEN=r.IMAGEN, REPARADOR=r.REPARADOR,
                    COMENTARIO=r.COMENTARIO, TrackID=r.TrackID, TestCode=r.TestCode
                )

            # --- Pendientes ---
            mod_PEND.consulta_Rechazos()
            rech = mod_PEND.process_Rechazos(download_folder / f"_Rechazos_{mod_PEND.file}")
            df_rech = rech if rech is not None else mod_PEND.pd.DataFrame()
            mod_PEND.consulta_Pendientes()
            mod_PEND.process_PENDIENTES(download_folder / mod_PEND.file, df_rech)
            df3 = mod_PEND.pd.read_excel(download_folder / mod_PEND.file)
            for r in df3.itertuples(index=False):
                Pendiente.objects.create(
                    MODELO=r.MODELO, NS=r.NS, FECHA_RECHAZO=r.FECHA_RECHAZO,
                    HORA_RECHAZO=r.HORA_RECHAZO, FUNCION=r.FUNCION,
                    CODIGO_FALLA=r.CODIGO_DE_FALLA_REPARACION,
                    CAUSA=r.CAUSA_DE_REPARACION, ORIGEN=r.ORIGEN, REPARADOR=r.REPARADOR
                )

            # --- YieldTurno ---
            turnos = mod_YT.pd.read_csv(mod_YT.links_url, dtype=str)
            dfs = []
            for row in turnos.itertuples(index=False):
                dfyt = mod_YT.consultaYield(row[0], row[3], row[4])
                if not dfyt.empty:
                    for r in dfyt.itertuples(index=False):
                        YieldTurno.objects.create(
                            Date=r.Date, Jornada=r.Jornada, Turno=r.Turno,
                            Line=r.Line, Family=r.Family, Process=r.Process,
                            Prime_Pass=r._7, Prime_Fail=r._8,
                            Prime_Handle=r._9, Prime_NTF_Count=r._10,
                            Prime_Defect_Count=r._11
                        )

            # --- Sampling (hoy, CQA, OQC) ---
            # Sampling-hoy
            dfsh = mod_SH.merge_html_files(download_folder)
            for r in dfsh.itertuples(index=False):
                Sampling.objects.create(tipo='hoy', Fecha=r.Fecha, Hora=r.Hora, dato=str(r._asdict()))

            # Sampling-CQA
            mod_SCQA.merge_html_files(download_folder, download_folder / mod_SCQA.file)
            dfsc = mod_SCQA.pd.read_excel(download_folder / mod_SCQA.file)
            for r in dfsc.itertuples(index=False):
                Sampling.objects.create(tipo='CQA', Fecha=r.Fecha, Hora=r.Hora, dato=str(r))

            # Sampling-OQC
            dfso = mod_SOQC.pd.read_excel(download_folder / mod_SOQC.file)
            for r in dfso.itertuples(index=False):
                Sampling.objects.create(tipo='OQC', Fecha=r.Fecha, Hora=r.Hora, dato=str(r))

            self.stdout.write(self.style.SUCCESS('🎉 Scraping completado y guardado en SQLite.'))

        except Exception as e:
            self.stderr.write(f"Error durante scraping: {e}")
            raise

        finally:
            browser.quit()

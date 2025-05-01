from pathlib import Path
import os, django, time
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException

os.environ.setdefault('DJANGO_SETTINGS_MODULE','Proyecto1.settings')
django.setup()
from quality.models import Pendiente
from App.entorno2 import firefox_service, firefox_option, download_folder, tmp_directory, wait_element, log_event, cargar_configuraciones, config_file_path

last=Pendiente.objects.order_by('-FECHA_RECHAZO','-HORA_RECHAZO').first()
if last:
    since_dt=datetime.combine(last.FECHA_RECHAZO,last.HORA_RECHAZO)+timedelta(seconds=1)
else:
    since_dt=datetime.now()-timedelta(days=28)
file='Pendientes.xlsx'

browser=webdriver.Firefox(service=firefox_service,options=firefox_option)
try:
    browser.get('http://motomes.newsan.com.ar/report/pendingByLocation')
    Select(wait_element(By.XPATH,'//select')).select_by_visible_text('Planta 4')
    wait_element(By.XPATH,'//input[contains(@placeholder,"Desde")]').click()
    wait_element(By.XPATH,f"//div[@title='{since_dt.strftime('%Y-%m-%d')}']").click()
    wait_element(By.XPATH,'//button[text()="Consultar"]').click()
    wait_element(By.XPATH,'//button[text()="Exportar"]',10).click()
    time.sleep(1)
    files=list(download_folder.glob('Reporte_Pendientes*.xlsx'))
    if files: files[0].rename(download_folder/file)
    log_event('info','Pendientes incremental OK')
finally:
    browser.quit()
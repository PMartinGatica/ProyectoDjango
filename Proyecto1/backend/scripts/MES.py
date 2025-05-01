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
from quality.models import MES
from App.entorno2 import firefox_service, firefox_option, download_folder, tmp_directory, wait_element, log_event, cargar_configuraciones, config_file_path

last = MES.objects.order_by('-FECHA_REPARACION','-HORA_REPARACION').first()
if last:
    since_dt = datetime.combine(last.FECHA_REPARACION, last.HORA_REPARACION)+timedelta(seconds=1)
else:
    since_dt = datetime.now()-timedelta(days=7)
file='MES.xlsx'

browser = webdriver.Firefox(service=firefox_service, options=firefox_option)
try:
    browser.get('http://motomes.newsan.com.ar/report/reparationsReportByLocation')
    # login si
    if 'login' in browser.current_url:
        cfg=cargar_configuraciones(config_file_path)
        e=browser.find_element(By.XPATH,'//input[@name="username"]'); e.send_keys(cfg['Usuario MES'])
        e=browser.find_element(By.XPATH,'//input[@name="password"]'); e.send_keys(cfg['Password MES']+Keys.ENTER)
        time.sleep(1)
    # seleccionar fechas
    Select(wait_element(By.XPATH,'//select')).select_by_visible_text('Planta 4')
    wait_element(By.XPATH,'//input[contains(@placeholder,"Desde")]').click()
    wait_element(By.XPATH,f"//div[@title='{since_dt.strftime('%Y-%m-%d')}']").click()
    wait_element(By.XPATH,'//input[contains(@placeholder,"Hasta")]').click()
    wait_element(By.XPATH,f"//div[@title='{datetime.now().strftime('%Y-%m-%d')}']").click()
    wait_element(By.XPATH,'//button[text()="Consultar"]').click()
    wait_element(By.XPATH,'//button[text()="Exportar"]',10).click()
    time.sleep(1)
    files=list(download_folder.glob('Reporte_Reparaciones*.xlsx'))
    if files:
        f=files[0]; f.rename(download_folder/file)
    log_event('info','MES incremental OK')
finally:
    browser.quit()

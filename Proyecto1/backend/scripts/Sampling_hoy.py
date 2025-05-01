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
from quality.models import Sampling
from App.entorno2 import firefox_service, firefox_option, download_folder, wait_element, log_event, cargar_configuraciones, config_file_path

# intervalo incremental
last_cqa = Sampling.objects.filter(tipo='CQA').order_by('-Fecha','-Hora').first()
last_oqc = Sampling.objects.filter(tipo='OQC').order_by('-Fecha','-Hora').first()
since_cqa = last_cqa.Fecha if last_cqa else datetime.today().date()
since_oqc = last_oqc.Fecha if last_oqc else datetime.today().date() - timedelta(days=7)
file='Sampling-hoy.xlsx'
cfg=cargar_configuraciones(config_file_path)
usser, password = cfg.get('usser_smp',''), cfg.get('pass_smp','')

# auxiliares ya definidas arriba: change_extension, process_html, merge_html

browser=webdriver.Firefox(service=firefox_service,options=firefox_option)
browser.get('http://10.30.10.111:100')
wait_element(By.XPATH,'//*[@id="nav"]/div[1]/h2').click()
wait_element(By.XPATH,'//*[@id="nav"]/div[1]/ul/li/a').click()
wait_element(By.ID,'TextBox1').send_keys(usser)
wait_element(By.ID,'TextBox2').send_keys(password+Keys.ENTER)
time.sleep(1)
try:
    # CQA hoy incremental
    browser.get('http://10.30.10.111:100/RegistroCqa.aspx')
    tbl=wait_element(By.ID,'ContentPlaceHolder1_GridView1')
    df1=pd.read_html(tbl.get_attribute('outerHTML'))[0]
    df1['Fecha']=pd.to_datetime(df1['Fecha']).dt.date
    df1=df1[df1['Fecha']>since_cqa]
    # descarga y merge similar al script CQA
    # OQC hoy incremental
    browser.get('http://10.30.10.111:100/registros.aspx')
    tbl2=wait_element(By.ID,'ContentPlaceHolder1_GridView1')
    df2=pd.read_html(tbl2.get_attribute('outerHTML'))[0]
    df2['Fecha']=pd.to_datetime(df2['Fecha']).dt.date
    df2=df2[df2['Fecha']>since_oqc]
    # procesar df2 similar a OQC script
    # guardar libro
    with pd.ExcelWriter(download_folder/file) as w:
        if not df1.empty: df1.to_excel(w,sheet_name='CQA',index=False)
        if not df2.empty: df2.to_excel(w,sheet_name='OQC',index=False)
    log_event('info','Sampling-hoy incremental OK')
finally:
    browser.quit()
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

# intervalo incremental para CQA
last = Sampling.objects.filter(tipo='CQA').order_by('-Fecha','-Hora').first()
since = last.Fecha if last else datetime.today().date() - timedelta(days=7)
file = 'Sampling-CQA.xlsx'
cfg = cargar_configuraciones(config_file_path)
usser, password = cfg.get('usser_smp',''), cfg.get('pass_smp','')

# funciones auxiliares

def change_extension(folder, ext):
    for f in folder.glob('Detalles-*.xls'):
        f.rename(f.with_suffix(ext))

def process_html(fp):
    txt = fp.read_text('latin1')
    return pd.read_html(txt)[0] if len(txt)>200 else None

def merge_html(folder, out):
    dfs=[]
    for h in folder.glob('Detalles-*.html'):
        df=process_html(h)
        if df is not None: dfs.append(df)
    if dfs:
        pd.concat(dfs).drop_duplicates().sort_values(['Fecha','Hora']).to_excel(out,index=False)

# main
browser=webdriver.Firefox(service=firefox_service,options=firefox_option)
browser.get('http://10.30.10.111:100')
wait_element(By.XPATH,'//*[@id="nav"]/div[1]/h2').click()
wait_element(By.XPATH,'//*[@id="nav"]/div[1]/ul/li/a').click()
wait_element(By.ID,'TextBox1').send_keys(usser)
wait_element(By.ID,'TextBox2').send_keys(password+Keys.ENTER)
time.sleep(1)

periodo = datetime.today().date()-timedelta(days=(datetime.today().date()-since).days)
try:
    browser.get('http://10.30.10.111:100/RegistroCqa.aspx')
    tbl=wait_element(By.ID,'ContentPlaceHolder1_GridView1')
    df=pd.read_html(tbl.get_attribute('outerHTML'))[0]
    df['Fecha']=pd.to_datetime(df['Fecha']).dt.date
    df=df[df['Fecha']>since]
    df['Link']=df['Registro'].apply(lambda x:f'http://10.30.10.111:100/DetalleCqa.aspx?variable1={x}')
    for url in df['Link'].dropna().unique():
        browser.get(url)
        wait_element(By.XPATH,'//*[@id="m1"]/div',60).click()
        wait_element(By.ID,'ContentPlaceHolder1_Button19',60).click()
    time.sleep(0.5)
    browser.quit()
    change_extension(download_folder,'.html')
    merge_html(download_folder,download_folder/file)
    log_event('info','Sampling-CQA incremental OK')
except Exception as e:
    log_event('error',f'Sampling-CQA error: {e}')
    browser.quit()
    raise

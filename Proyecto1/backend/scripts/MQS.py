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

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Proyecto1.settings')
django.setup()
from quality.models import MQS

# utilidades de entorno
from App.entorno2 import firefox_service, firefox_option, download_folder, tmp_directory, wait_element, log_event

# calcular intervalo incremental
last = MQS.objects.order_by('-Date','-Time').first()
if last:
    since_dt = datetime.combine(last.Date, last.Time) + timedelta(seconds=1)
else:
    since_dt = datetime.now() - timedelta(days=7)
start_str = since_dt.strftime('%m%d%Y')
end_str = datetime.now().strftime('%m%d%Y')
file = 'MQS.xlsx'
pickle_path = tmp_directory / 'TestCodes.pkl'
excel_path = download_folder / 'TestCodes.xlsx'
links_url = "https://docs.google.com/.../output=csv"


def campo_datetime(input_id, val):
    e = wait_element(By.ID, input_id)
    e.click()
    for _ in range(10): e.send_keys(Keys.LEFT)
    e.send_keys(val)


def paretoMQS():
    browser.get("https://mqs.motorola.com/NTF_Pareto2/Default10.aspx?")
    wait_element(By.ID,'LocationList').click()
    wait_element(By.XPATH,'//*[text()="MDB_TDF_Newsan"]').click()
    wait_element(By.ID,'RadioButton2').click()
    wait_element(By.ID,'PullTestVal').click()
    campo_datetime('Accordion_Normal_content_TextBox1', start_str)
    campo_datetime('Accordion_Normal_content_TextBox2', end_str)
    wait_element(By.ID,'Button3').click()
    wait_time = 30*((datetime.now()-since_dt).days)+150
    table = WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.ID,'GridView2')))
    WebDriverWait(browser, wait_time).until(lambda b: b.execute_script('return document.readyState')=='complete')
    return pd.read_html(table.get_attribute('outerHTML'))[0]


def process_MQS(df):
    if df.empty: return
    # extender fechas futuras si se desea...
    df['Date'] = pd.to_datetime(df['Date&Time']).dt.date
    df['Time'] = pd.to_datetime(df['Date&Time']).dt.time
    df['Line'] = df['Station'].str.split('-',1).str[0].fillna('')
    df = df.sort_values(['Date','Time'])
    df.to_excel(download_folder/file, index=False)

# ejecución
browser = webdriver.Firefox(service=firefox_service, options=firefox_option)
try:
    df = paretoMQS()
    process_MQS(df)
    log_event('info','MQS incremental OK')
finally:
    browser.quit()

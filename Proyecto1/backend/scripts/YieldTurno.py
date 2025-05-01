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
from quality.models import YieldTurno
from App.entorno2 import firefox_service, firefox_option, download_folder, wait_element, log_event, cargar_configuraciones, config_file_path

last=YieldTurno.objects.order_by('-Date').first()
if last: since_str=last.Date.strftime('%m%d%Y')
else: since_str=(datetime.now()-timedelta(days=1)).strftime('%m%d%Y')
file='YieldTurno.xlsx'
links_url='https://docs.google.com/spreadsheets/d/1ggV4P33PEc7sRgI4X426_7QK9Ria-4T1NByE49j4fRU/pub?output=csv'

browser=webdriver.Firefox(service=firefox_service,options=firefox_option)
try:
    df_links=pd.read_csv(links_url)
    df_links=df_links[df_links['Fecha']>=since_str]
    all=[]
    for _,r in df_links.iterrows():
        browser.get('https://mqs.motorola.com/Collab_GridCpt/default.aspx?')
        wait_element(By.ID,'LocationList').click();wait_element(By.XPATH,'//*[text()="MDB_TDF_Newsan"]').click()
        for btn in ['Line_Checked','NTF_Checked','DPHU']: wait_element(By.ID,btn).click()
        for fld,val in [('TextBox1',r['Fecha']),('TextBox2',r['Fecha']),('TextBox6',r['Desde']),('TextBox7',r['Hasta'])]: campo=wait_element(By.ID,fld);campo.click();campo.send_keys(val)
        wait_element(By.ID,'Button3').click()
        tbl=wait_element(By.ID,'GridView3',30)
        df=pd.read_html(tbl.get_attribute('outerHTML'))[0]
        df['Date']=datetime.strptime(r['Fecha'],'%m%d%Y').strftime('%Y-%m-%d')
        all.append(df[df['Family']!='***Total***'])
    if all:
        out=pd.concat(all)
        out.to_excel(download_folder/file,index=False)
        log_event('info','YieldTurno incremental OK')
finally: browser.quit()
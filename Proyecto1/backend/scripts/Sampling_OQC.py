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

last=Sampling.objects.filter(tipo='OQC').order_by('-Fecha','-Hora').first()
since=last.Fecha if last else datetime.today().date()-timedelta(days=7)
file='Sampling-OQC.xlsx'
cfg=cargar_configuraciones(config_file_path)
usser, password = cfg.get('usser_smp',''), cfg.get('pass_smp','')

browser=webdriver.Firefox(service=firefox_service,options=firefox_option)
browser.get('http://10.30.10.111:100')
wait_element(By.XPATH,'//*[@id="nav"]/div[1]/h2').click()
wait_element(By.XPATH,'//*[@id="nav"]/div[1]/ul/li/a').click()
wait_element(By.ID,'TextBox1').send_keys(usser)
wait_element(By.ID,'TextBox2').send_keys(password+Keys.ENTER)
time.sleep(1)

browser.get('http://10.30.10.111:100/registros.aspx')
df=pd.read_html(wait_element(By.ID,'ContentPlaceHolder1_GridView1').get_attribute('outerHTML'))[0]
df['Fecha']=pd.to_datetime(df['Fecha']).dt.date
df=df[df['Fecha']>since]
# luego proceso idéntico al script OQC anterior para descargar y guardar excel
browser.quit()
log_event('info','Sampling-OQC incremental OK')

#Recuerda instalar lxml en tu virtualenv para evitar errores de pd.read_html:ñ
#pip install lxml html5lib#
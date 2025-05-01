import logging, re, socket, time
from datetime import datetime, timedelta
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import presence_of_element_located, staleness_of
from selenium.webdriver.support import expected_conditions as EC

# Configuración inicial
start_time = time.time()
script_directory = Path(__file__).resolve().parent
parent_directory = script_directory.parent
download_folder = parent_directory / 'Data' / 'Descargas'
logs_directory = parent_directory / 'Data' / 'Logs'
tmp_directory = parent_directory / 'Data' / 'Temp'
config_file_path = parent_directory / 'Data/Credenciales.txt'
profile_directory = parent_directory / 'App/Profile'
firefox_path = str(parent_directory / 'App/Firefox/firefox.exe')
geckodriver_path = parent_directory / 'App/geckodriver.exe'

# Configura logging
file_log=logs_directory/f"{datetime.now().strftime('%Y-%m-%d')} {socket.gethostname()[-4:]} {parent_directory.name}.log"
logging.basicConfig(filename=file_log,level=logging.INFO,datefmt='%Y-%m-%d,%H:%M',
                    format='%(asctime)s,%(levelname)s,%(message)s')
logger = logging.getLogger(__name__)

def log_event(level, e):
    namepy = file.split(".")[0] if "." in file else file
    elapsed = round(time.time() - start_time, 2)
    if isinstance(e, UnexpectedAlertPresentException):
        alert_text = getattr(e, 'alert_text', None)
        message = f"Alert: {alert_text}" if not alert_text or "data available for this criteria" in alert_text else str(e)
        level = "warning"
    elif isinstance(e, TimeoutException):
        message = "Timeout occurred while waiting for the element."
        level = "error"
    else:
        message = str(e)
    message = (message.replace('//','/').replace('\\\\','\\').replace('-ahora',''))
    message = re.sub(r"(C:\\.*?\\)(App\\|Data\\|Tareas\\|Lib\\)", r'\2', message, flags=re.IGNORECASE)
    # message = re.split(r'File "App\\Python\\|Stacktrace:', message)[0]
    getattr(logger, level, logger.info)(f"{namepy},{elapsed},{message}")

def cargar_configuraciones(config_file_path):
    with open(config_file_path, "r") as archivo:
        return {clave.strip(): valor.strip() for clave, valor in (linea.strip().split(":") for linea in archivo)}

def wait_element(segundos, by, value):
    element = WebDriverWait(browser, segundos).until(EC.element_to_be_clickable((by, value)))
    return element

# Configurar Firefox con Selenium
log_path = str(logs_directory / 'geckodriver.log')
firefox_service = webdriver.firefox.service.Service(geckodriver_path)
firefox_option = webdriver.FirefoxOptions()
firefox_option.binary_location = firefox_path
firefox_option.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0')
firefox_option.set_preference("security.enterprise_roots.enabled", False)
firefox_option.add_argument('-profile')
firefox_option.add_argument(str(profile_directory))

# Configura la carpeta de descarga en el perfil, y desactiva la confirmacion de descarga.
firefox_option.set_preference('browser.download.folderList', 2)
firefox_option.set_preference("browser.download.alwaysOpenPanel", False)
#firefox_option.set_preference("toolkit.cosmeticAnimations.enabled", False)

firefox_option.set_preference('browser.download.manager.showWhenStarting', False)
firefox_option.set_preference('browser.download.panel.shown', False)
firefox_option.set_preference('browser.download.useToolkitUI', True)

firefox_option.set_preference('browser.download.dir', str(download_folder))
firefox_option.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')


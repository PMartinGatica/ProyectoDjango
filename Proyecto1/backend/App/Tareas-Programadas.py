import logging, re, socket, time
from datetime import datetime, timedelta
from pathlib import Path

import configparser
import subprocess
import schedule
import pandas as pd

bucle = 1 # MINUTOS CADA CUANTO EJECUTA EL BUCLE
dir_projet = Path(__file__).resolve().parent.parent
dir_logs = dir_projet / 'Data' / 'Logs'
semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

# Configura logging
file_log=dir_logs/f"{datetime.now().strftime('%Y-%m-%d')} {socket.gethostname()[-4:]} {dir_projet.name}.log"
logging.basicConfig(filename=file_log,level=logging.INFO,datefmt='%Y-%m-%d,%H:%M',
                    format='%(asctime)s,%(levelname)s,%(message)s')
logger = logging.getLogger(__name__)

def log_event(level, message):
    message = (message.replace('//','/').replace('\\\\','\\').replace('-ahora',''))
    message = re.sub(r"(C:\\.*?\\)(App\\|Data\\|Tareas\\|Lib\\)", r'\2', message, flags=re.IGNORECASE)
    message = re.split(r'File "App\\Python\\|Stacktrace:', message)[0]
    getattr(logger, level, logger.info)(f"Tareas-Programadas, ,{message}")

def planificar(script, frecuencia, unidad_tiempo, inicio):
    for script in script.split(','):
        script = script.strip()
        if unidad_tiempo == 'dias' or unidad_tiempo.lower() in semana:
            schedule.every().day.at(inicio).do(ejecutar, script, unidad_tiempo, inicio)
        elif unidad_tiempo == 'minutos':
            schedule.every(int(frecuencia)).minutes.do(ejecutar, script, unidad_tiempo, inicio)

def ejecutar(script, unidad_tiempo, inicio):
    inicio = datetime.strptime(inicio, "%H:%M").time()
    now = datetime.now().time()
    diferencia = (datetime.combine(datetime.min, inicio) - datetime.combine(datetime.min, now)).total_seconds() / 60
    hoy_dia = semana[datetime.now().weekday()].lower()
    resto_dias = [dia for dia in semana if dia != hoy_dia]
    if unidad_tiempo.lower() not in resto_dias and diferencia <= bucle:
        try:
            subprocess.run(['python', script])
        except Exception as e:
            log_event("error", f"Error al ejecutar el script {script}: {str(e)}")
            
try:
    with open(file_log, 'r') as file:
        data = [line.strip().split(',')[:6] for line in file]
    ejecutadas = pd.DataFrame(data, columns=['date','time','State','Script','TestTime','e'])
    ejecutadas_hoy = ejecutadas[ejecutadas['e'] == 'EXECUTED'].copy()
    ejecutadas_hoy['Script'] = ejecutadas_hoy['Script'].apply(lambda x: f"./Tareas/{x}.py")
    config = configparser.ConfigParser()
    config.read("Config.ini")
    sections = config.sections()
    current_time = datetime.now().time()

    for section in sections:
        script = config.get(section, 'script')
        frecuencia = config.get(section, 'frecuencia')
        unidad_tiempo = config.get(section, 'unidad_tiempo')
        inicio = config.get(section, 'inicio')
        # Verificar y ejecutar scripts atrasados
        if unidad_tiempo.lower() == 'dias' or unidad_tiempo.lower() in semana:
            inicio_time = datetime.strptime(inicio, "%H:%M").time()
            if inicio_time < current_time:
                for subscript in script.split(','):
                    subscript = subscript.strip()
                    if subscript == "./App/reset.py" or not ejecutadas_hoy[ejecutadas_hoy['Script'] == subscript].empty:
                        log_event("info", f"{subscript} no se ejecutó de nuevo, ya ejecutado a las {inicio}")
                    else:
                        log_event("warning", f"{subscript} ejecutado ahora, no ejecutado a las {inicio}")
                        ejecutar(subscript, unidad_tiempo, inicio)

        planificar(script, frecuencia, unidad_tiempo, inicio)
    while True:
        schedule.run_pending()
        time.sleep(bucle)
except Exception as e:
    log_event("error", f"Error en la ejecución: {str(e)}")
    raise e

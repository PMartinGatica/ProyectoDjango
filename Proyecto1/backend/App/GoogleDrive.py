import logging, os, re, shutil, socket, time
from datetime import datetime
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Configuración inicial
start_time = time.time()
parent_dir = Path(__file__).resolve().parent.parent
dir_data = parent_dir / 'Data'
download_folder = dir_data / 'Descargas'
logs_dir = dir_data / 'Logs'
config_file_path = dir_data / 'Credenciales.txt'

# Configura logging
file_log=logs_dir/f"{datetime.now().strftime('%Y-%m-%d')} {socket.gethostname()[-4:]} {parent_dir.name}.log"
logging.basicConfig(filename=file_log,level=logging.INFO,datefmt='%Y-%m-%d,%H:%M',
                    format='%(asctime)s,%(levelname)s,%(message)s')
logger = logging.getLogger(__name__)

def log_event(level, message):
    elapsed = round(time.time() - start_time, 2)
    processed_message = re.sub(r"(C:\\.*?\\)(App\\|Data\\|Tareas\\|Lib\\)", r'\2', str(message), flags=re.IGNORECASE)
    processed_message = re.sub(r"https://www\.googleapis\.com\S*(?=\s+returned)", "GoogleAPI", 
                               processed_message.split('File "App\\Python\\')[0], flags=re.IGNORECASE)
    processed_message = processed_message.replace('\n', ' ').replace('\r', ' ')
    processed_message = re.sub(r'\s+', ' ', processed_message)
    getattr(logger, level, logger.info)(f"GoogleDrive,{elapsed},{processed_message}")

def cargar_configuraciones(config_file_path):
    with open(config_file_path, "r") as archivo:
        return {clave.strip(): valor.strip() for clave, valor in (linea.strip().split(":") for linea in archivo)}

def authenticate_gdrive(dir_data):
    json_file = next(dir_data.glob('*.json'), None)
    creds = service_account.Credentials.from_service_account_file(json_file, scopes=['https://www.googleapis.com/auth/drive'])
    return build('drive', 'v3', credentials=creds, cache_discovery=False)

def list_files_in_folder(folder_path):
    return [file for file in folder_path.iterdir() if file.is_file()]

def upload_files(service, folder_id, file_name):
    metadata = {'name': file_name.stem, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
    media = MediaFileUpload(str(file_name), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resumable=True)
    response = service.files().list(q=f"name='{metadata['name']}' and '{folder_id}' in parents", fields='files(id)').execute()
    file_id = response.get('files', [])[0].get('id') if response.get('files', []) else None
    if file_id: # Si el archivo existe, lo actualizamos
        request = service.files().update(fileId=file_id, body=metadata, media_body=media)
    else: # Si el archivo no existe, lo creamos
        metadata['parents'] = [folder_id]
        request = service.files().create(body=metadata, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()

def get_folder_id(service, parent_folder_id, subfolder_name):
    response = service.files().list(
        q=f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{subfolder_name}'", fields='files(id)').execute()
    folders = response.get('files', [])
    return folders[0]['id'] if folders else None

def get_newest_file(folder_path):
    files = [file for file in folder_path.iterdir() if file.is_file()]
    return max(files, key=lambda x: x.stat().st_ctime)

def upload_newest_file(service, parent_folder_id, subfolder_name, file_path):
    subfolder_id = get_folder_id(service, parent_folder_id, subfolder_name)
    if not subfolder_id:
        metadata = {'name': subfolder_name, 'mimeType': 'application/vnd.google-apps.folder','parents': [parent_folder_id]}
        folder = service.files().create(body=metadata, fields='id').execute()
        subfolder_id = folder['id']
    response = service.files().list(q=f"'{subfolder_id}' in parents and name='{file_path.name}'", fields='files(id)').execute()
    files = response.get('files', [])
    if files:
        file_id = files[0]['id']
        media = MediaFileUpload(str(file_path), mimetype='text/plain', resumable=True)
        updated_file = service.files().update(fileId=file_id, media_body=media).execute()
    else:
        metadata = {'name': file_path.name, 'parents': [subfolder_id]}
        media = MediaFileUpload(str(file_path), mimetype='text/plain', resumable=True)
        new_file = service.files().create(body=metadata, media_body=media, fields='id').execute()

try:
    os.system(f'{'taskkill /f /im firefox.exe'} >nul 2>&1') # Mata Firefox
    
    log_messages = ""
    folder_id = cargar_configuraciones(config_file_path).get("ID de carpeta de Google Drive")
    service = authenticate_gdrive(dir_data)
    files_to_upload = list_files_in_folder(download_folder)

    for file_path in files_to_upload:
        if '_' in file_path.name:
            log_messages += f"Excluded {file_path.name} "
            continue
        upload_files(service, folder_id, file_path)
        log_messages += f"Uploaded {file_path.name} "

    subfolder_name = "Logs"
    log_files = list(sorted(logs_dir.iterdir(), key=lambda x: x.stat().st_ctime, reverse=True)[:2])

    today_str = datetime.now().strftime('%Y-%m-%d')
    for log_file in log_files:
        upload_newest_file(service, folder_id, subfolder_name, log_file)
        if log_file.is_file() and not log_file.name.startswith(today_str):
            log_file.unlink()
    
    time.sleep(0.5)
    shutil.rmtree(download_folder)
    download_folder.mkdir()

    log_event("info",log_messages)

except HttpError as e:
    if 'userRateLimitExceeded' in str(e):
        log_event("warning", f"Límite de tasa excedido: {e}")
    elif e.resp.status == 410:
        log_event("warning", f"URL de carga caducada: {e}")
    else:
        log_event("error", f"Error en la carga de archivos: {e}")
        raise
except Exception as e:
    log_event("error", e)

except HttpError as e:
    if 'userRateLimitExceeded' in str(e):
        log_event("warning", f"Límite de tasa excedido: {str(e)}")
    elif e.resp.status == 410:
        log_event("warning", f"URL de carga caducada: {str(e)}")
    else:
        log_event("error", f"Error en la carga de archivos: {str(e)}")
        raise
except Exception as e:
    log_event("error", str(e))

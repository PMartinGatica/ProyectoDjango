import urllib.request
import os
import zipfile
import io

# Descargar get-pip.py
url = "https://bootstrap.pypa.io/get-pip.py"
with urllib.request.urlopen(url) as response:
    script = response.read()

# Ejecutar el script para instalar pip
exec(script)

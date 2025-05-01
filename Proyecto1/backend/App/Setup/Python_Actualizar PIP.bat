cd /d "%~dp0"

:: Ejecuta el comando para listar las librerías instaladas
"..\Python\python.exe" -m pip install --upgrade pip
"..\Python\python.exe" -m pip cache purge

pause

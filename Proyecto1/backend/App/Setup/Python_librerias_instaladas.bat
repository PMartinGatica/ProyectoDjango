@echo off
cd /d "%~dp0"

:: Ejecuta el comando para listar las librerías instaladas
"..\Python\python.exe" -m pip list

pause

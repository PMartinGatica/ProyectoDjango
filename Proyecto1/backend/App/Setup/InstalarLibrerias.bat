@echo off
cd /d "%~dp0"

"..\Python\python.exe" -m pip install --upgrade pip

:: Ruta al archivo de configuracion con la lista de librerias
set "LIBS_FILE=.\libs.txt"

:: Leer librerias del archivo
setlocal enabledelayedexpansion
set "LIBS="
for /f "usebackq delims=" %%L in ("%LIBS_FILE%") do (
    set "LIBS=!LIBS! %%L"
)

:: Verificar e instalar cada libreria
for %%L in (%LIBS%) do (
    echo Verificando %%L...
    "..\Python\python.exe" -m pip show %%L >nul 2>&1
    if errorlevel 1 (
        echo %%L no esta instalada. Instalando...
        "..\Python\python.exe" -m pip install %%L
    ) else (
        echo %%L ya esta instalada.
    )
)

:: Limpiar cache de pip
echo Limpiando cache de pip...
"..\Python\python.exe" -m pip cache purge



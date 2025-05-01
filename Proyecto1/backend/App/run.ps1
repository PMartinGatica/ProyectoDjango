# Obtener directorios principales
$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$PythonExe = Join-Path $ScriptDir "Python\python.exe"
$BaseDir = Join-Path $ScriptDir "Setup\logs"
$Today = (Get-Date -Format "yyyy-MM-dd")
$UpdateLog = Join-Path $BaseDir "last_update.txt"
$InstallLog = Join-Path $BaseDir "install_log.txt"
$LibsFile = Join-Path $ScriptDir "Setup\libs.txt"

# Función para mensajes coloridos
function Write-ColoredMessage {
    param (
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Verificar y actualizar librerías
if (-not (Test-Path $UpdateLog) -or (Get-Content $UpdateLog -First 1) -ne $Today) {
    Write-ColoredMessage "#### VERIFICANDO LIBRERIAS ####`n" "Cyan"
    Clear-Content $InstallLog -ErrorAction SilentlyContinue

    if (Test-Path $LibsFile) {
        $Libraries = Get-Content $LibsFile | Where-Object { $_.Trim() -ne "" }

        foreach ($Library in $Libraries) {
            $status = if (& $PythonExe -m pip show $Library 2>&1 | Out-Null) {
                $upgradeOutput = & $PythonExe -m pip install --upgrade $Library 2>&1
                if ($upgradeOutput -match "Requirement already up-to-date") { "ya disponible" }
                else {
                    $upgradeOutput | Out-File $InstallLog -Append
                    "actualizado"
                }
            } else {
                $installOutput = & $PythonExe -m pip install $Library 2>&1
                if ($LASTEXITCODE -eq 0) { "instalado" }
                else {
                    $installOutput | Out-File $InstallLog -Append
                    "error en la instalacion"
                }
            }
            $Color = switch ($status) {
                "ya disponible" { "Green" }
                "actualizado"    { "Yellow" }
                "instalado"      { "Cyan" }
                default          { "Red" }
            }
            Write-Host ("{0,-30}" -f $Library) -NoNewline
            Write-Host $status -ForegroundColor $Color
        }
    } else {
        Write-ColoredMessage "Archivo de librerias no encontrado: $LibsFile`n" "Red"
    }

    Set-Content $UpdateLog $Today
} else {
    Write-ColoredMessage "Las librerias ya fueron verificadas hoy. Saltando la verificacion.`n" "Yellow"
}

# Limpieza y otras tareas
Write-ColoredMessage "#### LIMPIEZAS GENERALES ####`n" "Magenta"
Remove-Item "$ScriptDir\Profile" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "$ScriptDir\Profile" | Out-Null
Write-ColoredMessage "Perfil de Navegador reestablecido." "Green"

if (Test-Path "$ScriptDir\..\Data\Temp\mqs.pkl") {
    Remove-Item "$ScriptDir\..\Data\Temp\mqs.pkl" -Force
    Write-ColoredMessage "Se limpiaron archivos temporales." "Green"
}

# Verificar proceso KeepDisplayOn.exe
if (Get-Process -Name "KeepDisplayOn" -ErrorAction SilentlyContinue) {
    Write-ColoredMessage "KeepDisplayOn.exe ya estaba en ejecucion." "Yellow"
} else {
    Start-Process -FilePath "$ScriptDir\KeepDisplayOn.exe"
    Write-ColoredMessage "Se inicio KeepDisplayOn.exe para evitar que se apague el monitor." "Green"
}

# Limpiar cache pip
Write-ColoredMessage "Limpiando la cache pip...`n" "Cyan"
& $PythonExe -m pip cache purge

Write-ColoredMessage "########################################################" "Blue"
Write-ColoredMessage "        Se inicia el programador de scripts            " "White"
Write-ColoredMessage "########################################################" "Blue"

Exit 0

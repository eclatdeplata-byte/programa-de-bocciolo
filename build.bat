@echo off
REM build.bat - Construye el EXE usando el archivo de especificaciones de PyInstaller.

REM 1) Activa virtualenv si existe
if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
) else (
  echo No se detectó venv. Se recomienda crear uno:
  echo python -m venv venv && venv\Scripts\activate
)

REM 2) Limpia builds previos
rd /s /q build 2>nul
rd /s /q dist 2>nul

REM 3) Asegura PyInstaller instalado
python -m pip install --upgrade pip
python -m pip install pyinstaller PyQt5 pyqtgraph

REM 4) Comando PyInstaller usando el archivo .spec
pyinstaller --noconfirm --clean --onefile main.spec

if %ERRORLEVEL% NEQ 0 (
  echo PyInstaller falló. Revisa la salida arriba para errores.
  pause
  exit /b %ERRORLEVEL%
)

echo.
echo Build finalizado.
echo La carpeta 'dist' contiene 'main.exe'.
pause

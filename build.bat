@echo off
REM build.bat - Construye el EXE usando PyInstaller (Windows)
REM Ejecutar desde la carpeta del proyecto (donde está main.py, logo.png, productos.db, bocciolo_style.qss)

REM 1) Activa virtualenv si existe
if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
) else (
  echo No se detectó venv. Se recomienda crear uno:
  echo python -m venv venv && venv\Scripts\activate
)

REM 2) Limpia builds previos (opcional)
rd /s /q build 2>nul
rd /s /q dist 2>nul
del /q main.spec 2>nul

REM 3) Asegura PyInstaller instalado
python -m pip install --upgrade pip
python -m pip install pyinstaller PyQt5 pyqtgraph

REM 4) Comando PyInstaller para producción (sin consola)
REM La base de datos (productos.db) ya no se incluye DENTRO del exe.
REM Se copiará a la carpeta dist al final.
pyinstaller --noconfirm --clean --onefile --windowed ^
  --add-data "logo.png;." ^
  --add-data "bocciolo_style.qss;." ^
  main.py

if %ERRORLEVEL% NEQ 0 (
  echo PyInstaller falló. Revisa la salida arriba para errores.
  pause
  exit /b %ERRORLEVEL%
)

echo.
echo Build finalizado.
echo La carpeta 'dist' contiene 'main.exe'.
echo La base de datos se creará automáticamente en la primera ejecución.
pause

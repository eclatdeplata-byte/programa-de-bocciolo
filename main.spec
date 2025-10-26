# -*- mode: python ; coding: utf-8 -*-

# Este es un archivo de especificaciones de PyInstaller.
# Define cómo se debe empaquetar la aplicación, dando un control más preciso
# que los argumentos de línea de comandos.

block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('logo.png', '.'), ('bocciolo_style.qss', '.')],
             hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'sip'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,  # Equivale a --windowed
          runtime_tmpdir=None)

# La sentencia COLLECT es para empaquetado en modo de un solo directorio.
# Para el modo de un solo archivo (--onefile), no es necesaria.
# El ejecutable (exe) ya contiene todo lo necesario.

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# --- Hook definitivo para PyQt5 ---
# Este bloque utiliza la función más potente de PyInstaller, `collect_all`,
# para encontrar y empaquetar de forma exhaustiva todos los componentes de PyQt5,
# incluyendo binarios, datos y dependencias ocultas como 'sip'.
datas, binaries, hiddenimports = collect_all('PyQt5')
# --- Fin del Hook ---

a = Analysis(['main.py'],
             pathex=[],
             binaries=binaries,
             datas=[('logo.png', '.'), ('bocciolo_style.qss', '.')] + datas,
             hiddenimports=hiddenimports,
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )

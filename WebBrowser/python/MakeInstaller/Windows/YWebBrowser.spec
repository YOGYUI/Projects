import os
import sys
import pathlib

sys.setrecursionlimit(5000)

APP_NAME = 'YWebBrowser'
block_cipher = None

a = Analysis(['..\\..\\main.py'],
             pathex=['..\\..\\'],
             binaries=[],
             datas=[],
             hiddenimports=['PyQt5', 'PyQt5.QtWebEngineWidgets', 'pyautogui', 'bs4', 'requests',
                            'dateutil', 'dateutil.parser'],
             hookspath=['.\\hook'],
             runtime_hooks=[],
             excludes=['zmq', 'cv2', 'numpy', 'psutil', 'pillow'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher
          )

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name=APP_NAME,
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='..\\..\\Resource\\application.ico'
          )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=APP_NAME)

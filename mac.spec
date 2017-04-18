# -*- mode: python -*-


block_cipher = None


a = Analysis(['app.py'],
             pathex=['/Users/SlowWalker/Documents/Code/Project/xiamilist/github'],
             binaries=None,
             datas=[],
             hiddenimports=['queue'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[''],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='xiamilist',
          debug=False,
          strip=False,
          upx=True,
          console=False ,
          icon='/Users/SlowWalker/Documents/Code/Project/xiamilist/github/static/favicon.ico')

app = BUNDLE(exe,
         name='XiamiList.app',
         icon='/Users/SlowWalker/Documents/Code/Project/xiamilist/github/static/app.icns',
         bundle_identifier=None,
         info_plist={
            'NSHighResolutionCapable': 'True'
            },
         )
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src/aax2m4b.py'],
             pathex=['/Users/iwo16283/dev/ivonet-audiobook/'],
             binaries=[],
             datas=[
                ("src/resources", "./resources"),
                ("VERSION", "./resources"),
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='aax2m4b',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='aax2m4b')
app = BUNDLE(coll,
             name='aax2m4b.app',
             icon="./Yoda.icns",
             bundle_identifier=None,
             info_plist={
                'NSRequiresAquaSystemAppearance': 'No'
                },
             )

# -*- mode: python -*-
import sys

block_cipher = None

root_path = sys.prefix
tgt_gdal_data = os.path.join('Library', 'share', 'gdal')
src_gdal_data = os.path.join(root_path, 'Library', 'share', 'gdal')

a = Analysis(['find_duplicate_polygons.py'],
             pathex=['Z:\\mgleason\\github\\topochecks'],
             binaries=[],
             datas=[(src_gdal_data, tgt_gdal_data)],
             hiddenimports=['fiona._shim', 'json', 'fiona.schema'],
             hookspath=[],
             runtime_hooks=['runtime_hooks.py'],
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
          name='find_duplicate_polygons',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='find_duplicate_polygons')

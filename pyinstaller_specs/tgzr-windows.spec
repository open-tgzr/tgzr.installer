# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_entry_point

plugin_datas, plugin_hiddenimports = collect_entry_point('tgzr.cli.plugin')

# plugin_datas is like:
# >>>> [
#     (
#         '/home/dee/DEV/_OPEN-TGZR_/workspace_installer/.venv/lib/python3.12/site-packages/tgzr_session-0.0.1.dev1+g17b27f4a1.d20260427.dist-info', 
#         'tgzr_session-0.0.1.dev1+g17b27f4a1.d20260427.dist-info'
#     ), 
#     (
#         '/home/dee/DEV/_OPEN-TGZR_/workspace_installer/.venv/lib/python3.12/site-packages/tgzr_installer-0.0.1.dev1+gc26cee8a3.d20260426.dist-info',
#         'tgzr_installer-0.0.1.dev1+gc26cee8a3.d20260426.dist-info'
#     )
# ]
# plugin_hiddenimports is like:
# >>>> ['tgzr.session.plugins.cli_plugins', 'tgzr.installer.cli_plugins']

filtered_plugin_datas = []
filtered_hiddenimports = []
for data, hiddenimport in zip(plugin_datas, plugin_hiddenimports):
    print('?', data, hiddenimport)
    if not hiddenimport.startswith('tgzr.installer'):
        continue
    filtered_plugin_datas.append(data)
    filtered_hiddenimports.append(hiddenimport)

print('>>> ', filtered_plugin_datas)
print('>>> ', filtered_hiddenimports)

a = Analysis(
    ['../src/tgzr/installer/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('../.venv/Scripts/uv.exe', './bin')]+filtered_plugin_datas, # ! dont change this, see in tgzr.installer.install
    hiddenimports=[]+filtered_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='tgzr-install-windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

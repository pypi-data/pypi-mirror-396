# -*- mode: python ; coding: utf-8 -*-
import sys
import platform

block_cipher = None

# 根据平台决定是否显示控制台
# Windows 上不显示控制台，macOS/Linux 上显示（便于调试）
is_windows = platform.system() == 'Windows'

# 尝试收集 textual 和 rich 的所有模块和数据文件
try:
    from PyInstaller.utils.hooks import collect_all
    textual_datas, textual_binaries, textual_hiddenimports = collect_all('textual')
    rich_datas, rich_binaries, rich_hiddenimports = collect_all('rich')
except:
    # 如果 collect_all 失败，使用空列表
    textual_datas, textual_binaries, textual_hiddenimports = [], [], []
    rich_datas, rich_binaries, rich_hiddenimports = [], [], []

a = Analysis(
    ['km_search_tui.py'],
    pathex=[],
    binaries=textual_binaries + rich_binaries,
    datas=[('MasterDit.shp', '.')] + textual_datas + rich_datas,  # 包含词库文件和所有数据文件
    hiddenimports=textual_hiddenimports + rich_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 使用 onefile 模式，创建单个可执行文件（所有内容打包在一个文件中）
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='km_search',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=not is_windows,  # Windows 上不显示控制台，其他平台显示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
跨平台打包脚本
根据当前平台自动选择打包方式
"""

import sys
import platform
import subprocess
import os
from pathlib import Path

def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build():
    """执行打包"""
    system = platform.system()
    
    print(f"检测到系统: {system}")
    print("开始打包...")
    
    # 清理之前的构建
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
            print(f"已清理 {dir_name} 目录")
    
    # 执行打包
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "build.spec",
        "--noconfirm"
    ]
    
    subprocess.check_call(cmd)
    
    # 复制词库文件
    exe_name = "km_search.exe" if system == "Windows" else "km_search"
    dist_path = Path("dist") / "km_search"
    
    if (dist_path / exe_name).exists():
        import shutil
        shutil.copy("MasterDit.shp", dist_path)
        print(f"已复制词库文件到 {dist_path}")
    
    print("\n打包完成！")
    print(f"可执行文件位于: {dist_path / exe_name}")
    print("请确保 MasterDit.shp 文件与可执行文件在同一目录下")

def main():
    if not check_pyinstaller():
        install_pyinstaller()
    
    build()

if __name__ == "__main__":
    main()


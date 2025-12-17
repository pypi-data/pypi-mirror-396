#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
空明码查询工具入口点
"""

from km_search_tui import KMSearchApp
from pathlib import Path
import sys
import os


def km_search():
    """运行空明码查询应用"""
    # 获取词库文件路径
    # 尝试从多个位置查找词库文件
    dict_file = None
    
    # 1. 尝试从包数据目录读取（安装后的位置）
    try:
        import sys
        if sys.platform == "win32":
            import site
            # Windows: 尝试从 site-packages 的共享数据目录读取
            for site_dir in site.getsitepackages():
                data_file = Path(site_dir) / "share" / "km-search-tui" / "MasterDit.shp"
                if data_file.exists():
                    dict_file = data_file
                    break
        else:
            # Unix-like: 尝试从标准数据目录读取
            import site
            for site_dir in site.getsitepackages():
                data_file = Path(site_dir) / "share" / "km-search-tui" / "MasterDit.shp"
                if data_file.exists():
                    dict_file = data_file
                    break
    except:
        pass
    
    # 2. 尝试从当前工作目录读取
    if not dict_file or not dict_file.exists():
        dict_file = Path("MasterDit.shp")
        if not dict_file.exists():
            dict_file = None
    
    # 3. 尝试从用户主目录读取
    if not dict_file or not dict_file.exists():
        dict_file = Path.home() / "MasterDit.shp"
        if not dict_file.exists():
            dict_file = None
    
    if not dict_file or not dict_file.exists():
        print("错误: 找不到词库文件 MasterDit.shp")
        print("请将 MasterDit.shp 文件放在以下位置之一：")
        print("  1. 程序安装目录")
        print("  2. 当前工作目录")
        print("  3. 用户主目录")
        sys.exit(1)
    
    # 运行应用
    app = KMSearchApp(str(dict_file))
    app.run()


if __name__ == "__main__":
    km_search()


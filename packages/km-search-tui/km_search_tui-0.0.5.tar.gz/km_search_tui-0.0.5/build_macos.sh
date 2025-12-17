#!/bin/bash
set -e

echo "正在为 macOS 平台打包..."
echo ""

# 检查 PyInstaller 是否安装
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "正在安装 PyInstaller..."
    pip3 install pyinstaller
fi

# 清理之前的构建
rm -rf build dist

# 打包
echo "开始打包..."
pyinstaller --clean build.spec --noconfirm

# 添加执行权限
if [ -f "dist/km_search" ]; then
    chmod +x dist/km_search
fi

echo ""
echo "========================================"
echo "打包完成！"
echo "========================================"
echo "可执行文件位于: dist/km_search"
echo "词库文件已嵌入到可执行文件中，无需单独文件"
echo ""
echo "使用方法："
echo "  直接运行 ./dist/km_search 即可"
echo "  无需任何其他文件，所有内容都已打包在可执行文件中"
echo ""


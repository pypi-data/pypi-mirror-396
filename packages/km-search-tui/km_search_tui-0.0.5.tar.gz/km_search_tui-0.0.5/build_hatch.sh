#!/bin/bash
set -e

echo "正在使用 Hatch 打包..."
echo ""

# 检查 build 工具是否安装
if ! python3 -c "import build" 2>/dev/null; then
    echo "正在安装 build 工具..."
    pip3 install build
fi

# 清理之前的构建（保留 PyInstaller 的构建）
rm -f dist/km_search_tui-*.whl dist/km_search_tui-*.tar.gz
rm -rf build *.egg-info

# 构建
echo "开始构建..."
python3 -m build

echo ""
echo "========================================"
echo "打包完成！"
echo "========================================"
echo "构建文件位于 dist/ 目录"
echo ""
echo "安装方式："
echo "  1. 安装到当前环境: pip install dist/km_search_tui-0.1.0-py3-none-any.whl"
echo "  2. 安装到系统: pip install dist/km_search_tui-0.1.0-py3-none-any.whl"
echo "  3. 使用 pipx 安装: pipx install dist/km_search_tui-0.1.0-py3-none-any.whl"
echo ""
echo "安装后，可以使用以下命令运行："
echo "  km-search"
echo ""


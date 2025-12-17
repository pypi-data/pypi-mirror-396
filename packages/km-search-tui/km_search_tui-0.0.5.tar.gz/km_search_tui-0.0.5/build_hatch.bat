@echo off
chcp 65001 >nul
echo 正在使用 Hatch 打包...
echo.

REM 检查 build 工具是否安装
python -c "import build" 2>nul
if errorlevel 1 (
    echo 正在安装 build 工具...
    pip install build
)

REM 清理之前的构建（保留 PyInstaller 的构建）
if exist dist\km_search_tui-*.whl del /q dist\km_search_tui-*.whl
if exist dist\km_search_tui-*.tar.gz del /q dist\km_search_tui-*.tar.gz
if exist build rmdir /s /q build 2>nul
if exist *.egg-info rmdir /s /q *.egg-info 2>nul

REM 构建
echo 开始构建...
python -m build

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo 构建文件位于 dist\ 目录
echo.
echo 安装方式：
echo   1. 安装到当前环境: pip install dist\km_search_tui-0.1.0-py3-none-any.whl
echo   2. 安装到系统: pip install dist\km_search_tui-0.1.0-py3-none-any.whl
echo   3. 使用 pipx 安装: pipx install dist\km_search_tui-0.1.0-py3-none-any.whl
echo.
echo 安装后，可以使用以下命令运行：
echo   km-search
echo.
pause


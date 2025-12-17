@echo off
chcp 65001 >nul
echo 正在为 Windows 平台打包...
echo.

REM 检查并安装依赖
echo 检查依赖...
python -c "import textual" 2>nul
if errorlevel 1 (
    echo 正在安装 textual...
    pip install textual
)

python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

REM 清理之前的构建
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 打包
echo 开始打包...
pyinstaller --clean build.spec --noconfirm

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo 可执行文件位于: dist\km_search.exe
echo 词库文件已嵌入到可执行文件中，无需单独文件
echo.
echo 使用方法：
echo   直接运行 dist\km_search.exe 即可
echo   无需任何其他文件，所有内容都已打包在可执行文件中
echo.
pause


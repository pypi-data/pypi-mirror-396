# 打包说明

本项目支持为 Windows、macOS 和 Linux 三个平台打包成可执行文件。

## 前置要求

1. Python 3.14 或更高版本
2. 安装依赖：`pip install -r requirements.txt`
3. 确保 `MasterDit.shp` 词库文件在当前目录

## 打包方法

### 方法一：使用平台特定脚本（推荐）

#### Windows
```bash
build_windows.bat
```

#### macOS
```bash
chmod +x build_macos.sh
./build_macos.sh
```

#### Linux
```bash
chmod +x build_linux.sh
./build_linux.sh
```

### 方法二：使用 Python 脚本（自动检测平台）

```bash
python build_all.py
```

### 方法三：手动使用 PyInstaller

#### Windows
```bash
pyinstaller --clean build.spec --noconfirm
```

#### macOS/Linux
```bash
pyinstaller --clean build.spec --noconfirm
```

## 打包输出

打包完成后，可执行文件位于：
- Windows: `dist/km_search/km_search.exe`
- macOS/Linux: `dist/km_search/km_search`

## 注意事项

1. **词库文件**：打包后的可执行文件需要与 `MasterDit.shp` 文件在同一目录下才能正常运行
2. **文件大小**：由于包含了 Python 解释器和所有依赖，打包后的文件会比较大（约 50-100MB）
3. **首次运行**：首次运行可能需要几秒钟来解压和初始化
4. **权限**：在 macOS 和 Linux 上，可能需要给可执行文件添加执行权限：
   ```bash
   chmod +x dist/km_search/km_search
   ```

## 跨平台打包

如果你需要在不同平台上打包：

1. **Windows 打包**：在 Windows 系统上运行 `build_windows.bat`
2. **macOS 打包**：在 macOS 系统上运行 `./build_macos.sh`
3. **Linux 打包**：在 Linux 系统上运行 `./build_linux.sh`

或者使用 Docker 容器在不同平台上打包。

## 故障排除

### 问题：打包失败，提示找不到模块

**解决方案**：确保已安装所有依赖
```bash
pip install -r requirements.txt
```

### 问题：打包后的程序无法运行

**解决方案**：
1. 检查 `MasterDit.shp` 文件是否与可执行文件在同一目录
2. 在命令行中运行可执行文件查看错误信息
3. 确保系统满足 Python 3.14+ 的要求

### 问题：macOS 上打包后无法运行（安全限制）

**解决方案**：
```bash
# 移除隔离属性
xattr -cr dist/km_search/km_search
```


# 快速打包指南

## 一键打包（推荐）

### Windows
双击运行 `build_windows.bat` 或在命令行执行：
```cmd
build_windows.bat
```

### macOS
在终端执行：
```bash
chmod +x build_macos.sh && ./build_macos.sh
```

### Linux
在终端执行：
```bash
chmod +x build_linux.sh && ./build_linux.sh
```

## 打包前准备

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **确认词库文件**：
   确保 `MasterDit.shp` 文件在项目根目录

## 打包后

打包完成后，生成**单个可执行文件**：
- **Windows**: `dist\km_search.exe`
- **macOS/Linux**: `dist/km_search`

词库文件 `MasterDit.shp` 已嵌入到可执行文件中，无需单独文件。

## 分发

直接分发单个可执行文件即可（zip/tar.gz）。
用户无需安装 Python，无需任何其他文件，直接运行可执行文件即可。

## 详细说明

更多信息请查看：
- `BUILD.md` - 详细打包说明
- `PACKAGING.md` - 完整打包指南


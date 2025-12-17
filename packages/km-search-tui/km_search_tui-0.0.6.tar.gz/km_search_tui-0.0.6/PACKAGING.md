# 打包指南

## 快速开始

### Windows 平台

1. 打开命令提示符（CMD）或 PowerShell
2. 进入项目目录
3. 运行：
   ```cmd
   build_windows.bat
   ```
4. 打包完成后，可执行文件位于 `dist\km_search\km_search.exe`

### macOS 平台

1. 打开终端
2. 进入项目目录
3. 运行：
   ```bash
   chmod +x build_macos.sh
   ./build_macos.sh
   ```
4. 打包完成后，可执行文件位于 `dist/km_search/km_search`

### Linux 平台

1. 打开终端
2. 进入项目目录
3. 运行：
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```
4. 打包完成后，可执行文件位于 `dist/km_search/km_search`

## 打包步骤详解

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 确保词库文件存在

确保 `MasterDit.shp` 文件在项目根目录。

### 3. 执行打包

根据你的平台选择对应的打包脚本执行。

### 4. 测试打包结果

打包完成后，进入 `dist/km_search/` 目录，运行可执行文件测试。

## 打包输出说明

打包后生成**单个可执行文件**：
- **Windows**: `dist/km_search.exe`
- **macOS/Linux**: `dist/km_search`

词库文件 `MasterDit.shp` 已嵌入到可执行文件中，无需单独文件。

## 分发说明

要分发程序，只需要：
1. 将 `dist/km_search.exe`（Windows）或 `dist/km_search`（macOS/Linux）单独分发即可
2. 用户直接运行可执行文件即可，无需任何其他文件

**注意**：
- 用户不需要安装 Python 或任何依赖
- 词库文件已嵌入在可执行文件中
- 这是一个完全独立的单文件程序

## 常见问题

### Q: 打包后的文件很大？
A: 这是正常的，因为包含了完整的 Python 解释器和所有依赖库。通常大小在 50-100MB 左右。

### Q: 打包失败怎么办？
A: 
1. 确保已安装所有依赖：`pip install -r requirements.txt`
2. 确保 Python 版本 >= 3.14
3. 检查是否有足够的磁盘空间

### Q: 打包后的程序无法运行？
A:
1. 检查 `MasterDit.shp` 是否在可执行文件同一目录
2. 在命令行中运行查看错误信息
3. 确保系统满足最低要求

### Q: 如何在其他平台打包？
A: 你需要在对应的平台上运行打包脚本。例如：
- 在 Windows 上打包 Windows 版本
- 在 macOS 上打包 macOS 版本
- 在 Linux 上打包 Linux 版本

或者使用 Docker 容器在不同平台上打包。


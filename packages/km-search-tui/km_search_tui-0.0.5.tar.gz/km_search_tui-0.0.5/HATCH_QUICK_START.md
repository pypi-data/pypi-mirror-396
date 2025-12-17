# Hatch 打包快速开始

## 已完成的配置

✅ 项目已配置为 Hatch 打包格式
✅ 创建了包结构：`src/km_search_tui/`
✅ 配置了入口点：`km-search` 命令
✅ 配置了词库文件包含

## 快速打包

### Windows

```cmd
build_hatch.bat
```

或直接使用：
```cmd
pip install build
python -m build
```

### macOS/Linux

```bash
chmod +x build_hatch.sh
./build_hatch.sh
```

或直接使用：
```bash
pip3 install build
python3 -m build
```

## 构建结果

构建完成后，在 `dist/` 目录会生成：
- `km_search_tui-0.1.0-py3-none-any.whl` - Wheel 包（推荐）
- `km_search_tui-0.1.0.tar.gz` - 源码分发包

## 安装和使用

### 安装

```cmd
pip install dist\km_search_tui-0.1.0-py3-none-any.whl
```

或使用 pipx（推荐，避免依赖冲突）：
```cmd
pipx install dist\km_search_tui-0.1.0-py3-none-any.whl
```

### 运行

安装后，使用以下命令运行：
```cmd
km-search
```

## 词库文件

词库文件 `MasterDit.shp` 已包含在包中，安装后位于：
- Windows: `site-packages\share\km-search-tui\MasterDit.shp`
- Unix: `site-packages/share/km-search-tui/MasterDit.shp`

程序会自动查找词库文件，如果找不到会提示错误。

## 注意事项

- 如果路径包含中文字符，Hatch 可能遇到编码问题，建议使用 `python -m build` 代替
- 词库文件已通过 `shared-data` 配置自动包含
- 安装后无需额外配置，直接运行 `km-search` 即可


# 使用 Hatch 打包说明

## 问题说明

由于项目路径包含中文字符，Hatch 在构建时可能会遇到编码问题。以下是解决方案。

## 解决方案

### 方案一：移动到英文路径（推荐）

将项目复制到一个不包含中文的路径，例如：
```
C:\projects\km-search-tui\
```

然后在该目录执行打包。

### 方案二：使用环境变量

在打包前设置环境变量：
```cmd
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
hatch build
```

### 方案三：直接使用 pip 构建

如果 Hatch 无法正常工作，可以使用 pip 直接构建：

```cmd
pip install build
python -m build
```

## 项目结构

项目已配置为 Hatch 打包格式：

```
项目根目录/
├── src/
│   └── km_search_tui/
│       ├── __init__.py          # 主程序代码
│       └── entry_points.py      # 入口点
├── pyproject.toml               # Hatch 配置
├── MasterDit.shp               # 词库文件（会被包含）
└── README.md
```

## 打包步骤

1. **确保依赖已安装**：
   ```cmd
   pip install -r requirements.txt
   ```

2. **构建包**：
   ```cmd
   hatch build
   ```
   或使用 pip build：
   ```cmd
   pip install build
   python -m build
   ```

3. **构建结果**：
   构建完成后，会在 `dist/` 目录生成：
   - `km_search_tui-0.1.0.tar.gz` (源码分发包)
   - `km_search_tui-0.1.0-py3-none-any.whl` (wheel 包)

## 安装和使用

### 安装方式

1. **从本地 wheel 文件安装**：
   ```cmd
   pip install dist\km_search_tui-0.1.0-py3-none-any.whl
   ```

2. **使用 pipx 安装**（推荐，避免依赖冲突）：
   ```cmd
   pipx install dist\km_search_tui-0.1.0-py3-none-any.whl
   ```

3. **从源码安装**：
   ```cmd
   pip install dist\km_search_tui-0.1.0.tar.gz
   ```

### 运行程序

安装后，可以使用以下命令运行：
```cmd
km-search
```

## 词库文件位置

程序会按以下顺序查找词库文件 `MasterDit.shp`：

1. 安装包的共享数据目录：`site-packages/share/km-search-tui/MasterDit.shp`
2. 当前工作目录：`./MasterDit.shp`
3. 用户主目录：`~/MasterDit.shp`

如果找不到词库文件，程序会提示错误信息。

## 发布到 PyPI（可选）

如果要将应用发布到 PyPI：

1. **创建 PyPI 账户**（如果还没有）

2. **创建 API Token**：
   - 登录 PyPI
   - 进入 Account Settings
   - 创建 API Token

3. **发布**：
   ```cmd
   hatch publish -u __token__ -a <YOUR_API_TOKEN>
   ```

## 注意事项

- 词库文件 `MasterDit.shp` 会通过 `shared-data` 配置包含在 wheel 包中
- 安装后，词库文件位于 `site-packages/share/km-search-tui/` 目录
- 如果路径包含中文字符，建议移动到英文路径再打包


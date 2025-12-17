# PyPI OIDC 自动发布配置指南

本指南说明如何配置使用 OIDC（OpenID Connect）的 GitHub Actions 自动发布到 PyPI。

## 前置条件

1. 在 PyPI 上已有项目（如果没有，需要先创建）
2. 拥有项目的管理权限

## 配置步骤

### 1. 在 PyPI 上配置 Trusted Publisher

1. 登录 [PyPI](https://pypi.org)
2. 进入你的项目页面，点击 **"Manage"** 按钮
3. 在左侧边栏点击 **"Publishing"**
4. 在 "Trusted Publishers" 部分，点击 **"Add a new trusted publisher"**
5. 选择 **"GitHub Actions"** 标签页
6. 填写以下信息：
   - **PyPI project name**: `km-search-tui`（你的项目名称）
   - **Owner**: 你的 GitHub 用户名或组织名
   - **Repository name**: `km-search-tui`（你的仓库名称）
   - **Workflow filename**: `publish.yml`（工作流文件名）
   - **Environment name**（可选，但强烈推荐）: `pypi`
7. 点击 **"Add"** 完成配置

### 2. 配置 GitHub Environment（可选但推荐）

为了增加安全性，建议配置 GitHub Environment：

1. 在 GitHub 仓库中，进入 **Settings** → **Environments**
2. 点击 **"New environment"**
3. 输入环境名称：`pypi`
4. 在 "Required reviewers" 中添加需要审批的人员
5. 保存环境配置

### 3. 更新工作流文件（如果使用了 Environment）

如果你配置了 GitHub Environment，需要更新 `.github/workflows/publish.yml` 文件，在发布步骤中添加环境：

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: dist/
    print-hash: true
  environment:
    name: pypi
```

## 使用方法

### 方法一：通过 GitHub Release 发布（推荐）

1. 更新 `pyproject.toml` 中的版本号
2. 提交并推送代码：
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to x.y.z"
   git push
   ```
3. 创建 GitHub Release：
   - 在 GitHub 仓库页面，点击 **"Releases"** → **"Create a new release"**
   - 选择或创建新标签（如 `v0.1.0`）
   - 填写发布说明
   - 点击 **"Publish release"**
4. GitHub Actions 会自动触发，构建并发布到 PyPI

### 方法二：手动触发工作流

1. 在 GitHub 仓库页面，进入 **Actions** 标签页
2. 选择 **"Publish to PyPI"** 工作流
3. 点击 **"Run workflow"**
4. 输入版本号
5. 点击 **"Run workflow"** 按钮

## 验证发布

发布完成后，可以在以下位置验证：

1. **PyPI 项目页面**: https://pypi.org/project/km-search-tui/
2. **GitHub Actions 日志**: 查看工作流运行日志
3. **安装测试**:
   ```bash
   pip install km-search-tui
   ```

## 安全说明

- ✅ 使用 OIDC 无需在 GitHub Secrets 中存储 API token
- ✅ 每次发布都会生成短期令牌，自动过期
- ✅ 如果配置了 Environment，发布需要审批才能执行
- ✅ 只有配置的仓库和工作流才能发布

## 故障排除

### 问题：发布失败，提示 "No trusted publisher found"

**解决方案**：
- 检查 PyPI 上的 Trusted Publisher 配置是否正确
- 确认仓库名称、工作流文件名是否匹配
- 确认 GitHub Actions 有 `id-token: write` 权限

### 问题：发布失败，提示 "Environment protection rules"

**解决方案**：
- 如果配置了 Environment，需要先审批
- 或者移除 Environment 配置

### 问题：版本已存在

**解决方案**：
- 更新 `pyproject.toml` 中的版本号
- 重新提交并发布

## 参考文档

- [PyPI Trusted Publishers 文档](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
- [pypa/gh-action-pypi-publish 文档](https://github.com/pypa/gh-action-pypi-publish)


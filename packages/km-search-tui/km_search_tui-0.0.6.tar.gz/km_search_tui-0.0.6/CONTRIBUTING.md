# 贡献指南

感谢你考虑为 km-search-tui 项目做贡献！

## 开发流程

### 1. Fork 项目
从 GitHub 仓库 fork 项目到你的个人账户。

### 2. Clone 仓库
```bash
git clone https://github.com/your-username/km-search-tui.git
cd km-search-tui
```

### 3. 创建分支
```bash
git checkout -b feature/your-feature-name
```

### 4. 开发
- 遵循代码规范
- 使用 emoji conventional commits
- 编写测试用例（如果需要）

### 5. 提交更改
```bash
git add .
git commit -m "✅ feat: 添加新功能"
```

### 6. 推送到你的 fork
```bash
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request
在 GitHub 上创建 PR，描述你的更改。

## 代码规范

### Python 代码
- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 最大行长度 88 字符
- 使用类型注解

### Commit Message 规范
请参考 [`.git-commit-template.txt`](.git-commit-template.txt)

### 文档
- 所有公共函数需要文档字符串
- 复杂逻辑需要注释
- 保持 README 更新

## 提交规范

本项目使用 emoji conventional commits：

- ✅ feat: 新功能
- 🐛 fix: Bug 修复
- 📚 docs: 文档更新
- 💄 style: 代码格式
- 🧹 refactor: 重构
- 🧪 test: 测试
- ⚙️ chore: 构建工具变更
- 🚀 perf: 性能优化
- 🎯 release: 发布
- ❌ revert: 回滚

## 发布流程

1. 所有更改需要在 develop 分支上
2. 推送到 develop 分支触发 CI/CD
3. 创建 release 分支触发自动发布
4. 自动构建和发布到 PyPI

## 测试

- 运行测试：`pytest`
- 代码覆盖率：`pytest --cov=src`
- 类型检查：`mypy src`

## 问题反馈

- 使用 GitHub Issues 报告 bug
- 提供详细的重现步骤
- 附上相关日志和截图

## 联系方式

- GitHub Issues: [项目 Issues 页面](https://github.com/kongmingma/km-search-tui/issues)
- Email: [项目维护者邮箱]

感谢你的贡献！
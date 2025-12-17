# 发布指南 / Publishing Guide

## NPM 包发布

### 准备工作

1. 确保所有测试通过
2. 更新版本号和 CHANGELOG
3. 构建项目

```bash
npm run build
npm test
```

### 发布步骤

```bash
# 登录 NPM
npm login

# 发布包
npm publish

# 如果是第一次发布公共包
npm publish --access public
```

### 版本管理

使用语义化版本（Semantic Versioning）：

```bash
# 补丁版本（bug 修复）
npm version patch

# 次要版本（新功能，向后兼容）
npm version minor

# 主要版本（破坏性变更）
npm version major
```

## GitHub Release

### 创建发布

1. 推送标签：
```bash
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0
```

2. 在 GitHub 上创建 Release：
   - 转到仓库的 Releases 页面
   - 点击 "Draft a new release"
   - 选择刚创建的标签
   - 填写发布说明
   - 发布

### 自动化发布

项目已配置 GitHub Actions，推送标签后会自动：
- 运行测试
- 构建项目
- 创建 Release
- 发布到 NPM（需配置 `NPM_TOKEN` secret）

## Docker 镜像发布（可选）

如果需要提供 Docker 镜像：

```bash
# 构建镜像
docker build -t mijia-mcp-server:2.0.0 .

# 推送到 Docker Hub
docker tag mijia-mcp-server:2.0.0 yourusername/mijia-mcp-server:2.0.0
docker push yourusername/mijia-mcp-server:2.0.0
```

## 发布检查清单

- [ ] 更新版本号（package.json, __init__.py）
- [ ] 更新 CHANGELOG.md
- [ ] 运行完整测试套件
- [ ] 更新文档
- [ ] 构建项目无错误
- [ ] 提交所有更改
- [ ] 创建 Git 标签
- [ ] 推送到 GitHub
- [ ] 发布到 NPM
- [ ] 创建 GitHub Release
- [ ] 更新示例配置

## 回滚发布

如果发现问题需要回滚：

```bash
# 撤销 NPM 发布（24小时内）
npm unpublish mijia-mcp-server@2.0.0

# 或标记为废弃
npm deprecate mijia-mcp-server@2.0.0 "Critical bug, please use 2.0.1"
```

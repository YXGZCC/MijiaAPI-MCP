# GitHub 推送指南

## ✅ 已完成的配置

1. **Git 用户信息已配置**
   - 用户名: `YXGZCC`
   - 邮箱: `yxgzcc@qq.com`

2. **远程仓库地址已更新**
   - 原地址: `https://github.com/chenziCY/20251216173558.git`
   - 新地址: `https://github.com/YXGZCC/MijiaAPI-MCP.git`

3. **代码已提交**
   - 最新提交: `docs: 添加功能测试报告并更新 .gitignore`
   - 更新了 `.gitignore` 文件
   - 添加了 `TEST_REPORT.md` 测试报告

## 🚀 推送到 GitHub

### 方法一：使用 GitHub CLI（推荐）

如果已安装 GitHub CLI (`gh`):

```bash
# 登录 GitHub
gh auth login

# 推送代码
git push -u origin main
```

### 方法二：使用 Personal Access Token (PAT)

1. **创建 Personal Access Token**
   - 访问: https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 勾选 `repo` 权限
   - 生成并复制 Token

2. **使用 Token 推送**

```bash
# 推送时会提示输入用户名和密码
git push -u origin main

# 输入：
# Username: YXGZCC
# Password: [粘贴你的 Personal Access Token]
```

### 方法三：使用 SSH（更安全）

1. **生成 SSH 密钥**（如果还没有）

```bash
ssh-keygen -t ed25519 -C "yxgzcc@qq.com"
# 按 Enter 使用默认路径
```

2. **添加 SSH 密钥到 GitHub**
   - 复制公钥内容:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   - 访问: https://github.com/settings/ssh/new
   - 粘贴公钥并保存

3. **更改仓库为 SSH 地址**

```bash
git remote set-url origin git@github.com:YXGZCC/MijiaAPI-MCP.git
git push -u origin main
```

## 📝 当前状态

```
本地分支: main
远程仓库: https://github.com/YXGZCC/MijiaAPI-MCP.git
待推送提交: 2 个 (first commit + 最新更新)
```

## 🔍 验证推送成功

推送成功后，访问你的仓库:
https://github.com/YXGZCC/MijiaAPI-MCP

应该能看到:
- ✅ README.md
- ✅ TEST_REPORT.md（新添加）
- ✅ 所有项目文件
- ✅ 提交历史

## ⚠️ 注意事项

1. **首次推送**需要身份验证
2. **推荐使用 SSH** 方式，一次配置永久使用
3. **不要使用密码**认证（GitHub 已禁用），必须使用 Token 或 SSH
4. `.gitignore` 已更新，不会推送 `node_modules/`, `.venv/`, `__pycache__/` 等文件

## 🆘 遇到问题？

**提示"Support for password authentication was removed"**
→ 使用 Personal Access Token 或 SSH

**推送被拒绝 (rejected)**
→ 可能是新仓库有 README，先执行:
```bash
git pull origin main --rebase
git push -u origin main
```

**权限被拒绝**
→ 检查 Token 权限或 SSH 密钥配置

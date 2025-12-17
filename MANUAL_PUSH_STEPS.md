# 手动推送步骤

由于自动推送可能需要交互，请按以下步骤手动执行：

## 📝 在终端中执行以下命令

```bash
# 1. 进入项目目录
cd c:\Users\chenz\CodeBuddy\MijiaAPI-MCP

# 2. 获取远程更新
git fetch origin

# 3. 合并远程内容（会打开编辑器，直接保存退出即可）
git merge origin/main --allow-unrelated-histories

# 4. 添加推送指南文档
git add PUSH_GUIDE.md

# 5. 提交
git commit -m "docs: 添加 GitHub 推送指南"

# 6. 推送到 GitHub
git push -u origin main
```

## ✅ SSH 验证已通过

```
✓ SSH 配置正常
✓ 远程仓库: git@github.com:YXGZCC/MijiaAPI-MCP.git
✓ 身份验证: YXGZCC
```

## 🎯 完成后验证

推送成功后，访问: https://github.com/YXGZCC/MijiaAPI-MCP

应该能看到所有文件和提交记录。

## ⚠️ 如果第3步出现冲突

如果合并时出现冲突，执行：
```bash
# 查看冲突文件
git status

# 解决冲突后
git add .
git commit -m "merge: 合并远程分支"
git push -u origin main
```

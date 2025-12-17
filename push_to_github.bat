@echo off
echo ===================================
echo 推送代码到 GitHub
echo ===================================
echo.

cd /d %~dp0

echo [1/4] 获取远程更新...
git fetch origin

echo.
echo [2/4] 合并远程内容（允许不相关历史）...
git pull origin main --allow-unrelated-histories --no-edit

echo.
echo [3/4] 添加推送指南...
git add PUSH_GUIDE.md

echo.
echo [4/4] 推送到远程仓库...
git push -u origin main

echo.
echo ===================================
echo 推送完成！
echo 访问仓库: https://github.com/YXGZCC/MijiaAPI-MCP
echo ===================================
pause

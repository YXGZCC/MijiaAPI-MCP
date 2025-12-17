#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布辅助脚本
自动化版本更新、标签创建和发布流程
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Tuple


def get_current_version() -> str:
    """从 __init__.py 读取当前版本"""
    init_file = Path("__init__.py")
    content = init_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    return "0.0.0"


def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> None:
    """更新文件中的版本号"""
    content = file_path.read_text(encoding="utf-8")
    content = content.replace(old_version, new_version)
    file_path.write_text(content, encoding="utf-8")
    print(f"✓ 已更新 {file_path}")


def parse_version(version: str) -> Tuple[int, int, int]:
    """解析版本号"""
    parts = version.split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_version(version: str, bump_type: str) -> str:
    """递增版本号"""
    major, minor, patch = parse_version(version)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def run_command(cmd: str) -> bool:
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 命令失败: {result.stderr}")
        return False
    print(result.stdout)
    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python release.py [major|minor|patch|<version>]")
        print("示例:")
        print("  python release.py patch    # 2.0.0 -> 2.0.1")
        print("  python release.py minor    # 2.0.0 -> 2.1.0")
        print("  python release.py major    # 2.0.0 -> 3.0.0")
        print("  python release.py 2.5.0    # 直接指定版本")
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"当前版本: {current_version}")
    
    version_arg = sys.argv[1]
    if version_arg in ["major", "minor", "patch"]:
        new_version = bump_version(current_version, version_arg)
    else:
        new_version = version_arg
    
    print(f"新版本: {new_version}")
    confirm = input("继续? (y/N): ")
    if confirm.lower() != "y":
        print("已取消")
        sys.exit(0)
    
    # 更新版本号
    files_to_update = [
        Path("__init__.py"),
        Path("package.json"),
        Path("pyproject.toml"),
    ]
    
    for file_path in files_to_update:
        if file_path.exists():
            update_version_in_file(file_path, current_version, new_version)
    
    # 构建项目
    print("\n构建项目...")
    if not run_command("npm run build"):
        print("❌ 构建失败")
        sys.exit(1)
    
    # 提交更改
    print("\n提交更改...")
    run_command("git add .")
    run_command(f'git commit -m "chore: bump version to {new_version}"')
    
    # 创建标签
    print("\n创建标签...")
    run_command(f'git tag -a v{new_version} -m "Release version {new_version}"')
    
    print(f"\n✓ 版本已更新到 {new_version}")
    print("\n下一步:")
    print(f"  git push origin main")
    print(f"  git push origin v{new_version}")
    print(f"  npm publish")


if __name__ == "__main__":
    main()

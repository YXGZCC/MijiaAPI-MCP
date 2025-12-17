#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Python 环境
"""
import sys
import json
import platform

def test_environment(args):
    """测试 Python 环境和库"""
    try:
        result = {
            "success": True,
            "python_version": platform.python_version(),
            "python_path": sys.executable,
            "platform": platform.platform(),
            "installed_packages": []
        }
        
        # 测试基础库
        try:
            import requests
            result["installed_packages"].append(f"requests {requests.__version__}")
        except ImportError:
            result["installed_packages"].append("requests - NOT INSTALLED")
        
        try:
            import aiohttp
            result["installed_packages"].append(f"aiohttp {aiohttp.__version__}")
        except ImportError:
            result["installed_packages"].append("aiohttp - NOT INSTALLED")
        
        # 尝试导入 miservice
        try:
            import miservice
            result["installed_packages"].append("miservice - INSTALLED")
            result["miservice_available"] = True
        except ImportError as e:
            result["installed_packages"].append(f"miservice - NOT INSTALLED ({str(e)})")
            result["miservice_available"] = False
        
        # 尝试导入 mijiaAPI
        try:
            import mijiaAPI
            version = getattr(mijiaAPI, '__version__', 'unknown')
            result["installed_packages"].append(f"mijiaAPI {version} - INSTALLED ✅")
            result["mijia_available"] = True
            
            # 检查可用的类和函数
            result["mijia_classes"] = [name for name in dir(mijiaAPI) if not name.startswith('_')]
        except ImportError as e:
            result["installed_packages"].append(f"mijiaAPI - NOT INSTALLED ({str(e)})")
            result["mijia_available"] = False
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    args_json = sys.argv[1] if len(sys.argv) > 1 else "{}"
    args = json.loads(args_json)
    
    result = test_environment(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))

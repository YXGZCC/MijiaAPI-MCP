#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取米家智能设备列表（真实版本 - 使用 mijiaAPI）
"""
import sys
import json
from mijiaAPI import mijiaAPI

def get_mijia_devices(args):
    """
    获取米家设备列表
    需要配置米家账号信息
    """
    try:
        # 从参数或环境变量读取账号信息
        username = args.get("username") or "your_username"
        password = args.get("password") or "your_password"
        
        # 初始化米家 API
        api = mijiaAPI(username, password)
        
        # 登录
        if not api.login():
            return {
                "success": False,
                "error": "登录失败，请检查账号密码"
            }
        
        # 获取设备列表
        devices = api.get_devices()
        
        result = {
            "success": True,
            "devices": [
                {
                    "id": device.get("did"),
                    "name": device.get("name"),
                    "model": device.get("model"),
                    "online": device.get("isOnline", False),
                    "room": device.get("roomName", "未分配"),
                }
                for device in devices
            ],
            "total": len(devices)
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"错误: {str(e)}"
        }

if __name__ == "__main__":
    # 从命令行参数获取输入
    args_json = sys.argv[1] if len(sys.argv) > 1 else "{}"
    args = json.loads(args_json)
    
    # 调用函数并输出结果
    result = get_mijia_devices(args)
    print(json.dumps(result, ensure_ascii=False))

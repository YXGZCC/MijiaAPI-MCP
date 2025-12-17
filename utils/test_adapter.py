#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试适配器功能
验证 mijia_adapter 和 mijia_tool 能否正常工作
"""

import sys
import json
from pathlib import Path

# 添加 adapter 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "adapter"))

try:
    from mijia_adapter import MijiaController, DeviceIdentifier
    from mijia_tool import handle_action
    
    print("✓ 成功导入适配器模块")
    
    # 测试 Mock 模式
    print("\n测试 Mock 模式...")
    
    # 测试列出家庭
    result = handle_action("list_homes", {"use_mock": True})
    print(f"✓ list_homes: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试列出设备
    result = handle_action("list_devices", {"use_mock": True})
    print(f"✓ list_devices: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试获取设备状态
    result = handle_action("device_status", {
        "use_mock": True,
        "device_name": "卧室台灯"
    })
    print(f"✓ device_status: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    print("\n✅ 所有适配器测试通过！")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""保持向后兼容的设备状态脚本，调用统一的 mijia_tool。"""
import json
import sys

from mijia_tool import handle_action

if __name__ == "__main__":
    payload = sys.argv[1] if len(sys.argv) > 1 else "{}"
    args = json.loads(payload)
    args.setdefault("action", "device_status")
    try:
        result = handle_action("device_status", args)
    except Exception as exc:  # noqa: BLE001
        result = {"success": False, "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False))


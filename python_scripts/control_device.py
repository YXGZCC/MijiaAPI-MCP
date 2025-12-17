#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""保持向后兼容的控制脚本，委托给 mijia_tool 处理。"""
import json
import sys

from mijia_tool import handle_action

if __name__ == "__main__":
    payload = sys.argv[1] if len(sys.argv) > 1 else "{}"
    args = json.loads(payload)
    args.setdefault("action", "control_device")
    try:
        result = handle_action("control_device", args)
    except Exception as exc:  # noqa: BLE001
        result = {"success": False, "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False))


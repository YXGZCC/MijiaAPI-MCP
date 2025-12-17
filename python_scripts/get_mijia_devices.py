#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""保持向后兼容的设备列表脚本，实际逻辑委托给 mijia_tool。"""
import json
import sys

from mijia_tool import handle_action

if __name__ == "__main__":
    payload = sys.argv[1] if len(sys.argv) > 1 else "{}"
    args = json.loads(payload)
    args.setdefault("action", "list_devices")
    try:
        result = handle_action("list_devices", args)
    except Exception as exc:  # noqa: BLE001
        result = {"success": False, "error": str(exc)}
    print(json.dumps(result, ensure_ascii=False))


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一的米家工具脚本，根据 action 调用不同的 API 功能。"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from mijia_adapter import (
    DeviceIdentifier,
    MijiaController,
    build_controller,
    handle_exception,
    success_response,
)


def _ensure_identifier(args: Dict[str, Any]) -> DeviceIdentifier:
    device_id = args.get("device_id")
    device_name = args.get("device_name") or args.get("dev_name")
    if not device_id and not device_name:
        raise ValueError("需要提供 device_id 或 device_name")
    return DeviceIdentifier(did=device_id, name=device_name)


def _bool_arg(args: Dict[str, Any], key: str, default: bool = False) -> bool:
    value = args.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def handle_action(action: str, args: Dict[str, Any]) -> Dict[str, Any]:
    controller: MijiaController = build_controller(args)

    if action == "list_homes":
        homes = controller.list_homes()
        return success_response(data=homes)

    if action == "list_devices":
        home_id = args.get("home_id")
        include_shared = _bool_arg(args, "include_shared", False)
        devices = controller.list_devices(home_id=home_id, include_shared=include_shared)
        return success_response(data=devices)

    if action == "device_status":
        identifier = _ensure_identifier(args)
        properties = args.get("properties")
        include_metadata = _bool_arg(args, "include_metadata", True)
        result = controller.get_device_status(identifier, properties=properties, include_metadata=include_metadata)
        return success_response(**result)

    if action == "control_device":
        identifier = _ensure_identifier(args)
        operation = args.get("operation", "set_property")
        prop_name = args.get("prop_name")
        value = args.get("value")
        action_name = args.get("action_name")
        action_value = args.get("action_value")
        action_kwargs = args.get("action_kwargs") or args.get("params")
        result = controller.control_device(
            identifier,
            operation=operation,
            prop_name=prop_name,
            value=value,
            action_name=action_name,
            action_value=action_value,
            action_kwargs=action_kwargs,
        )
        return success_response(**result)

    if action == "list_scenes":
        home_id = args.get("home_id")
        scenes = controller.list_scenes(home_id=home_id)
        return success_response(data=scenes)

    if action == "run_scene":
        scene_id = args.get("scene_id")
        home_id = args.get("home_id")
        if not scene_id or not home_id:
            raise ValueError("运行场景需要提供 scene_id 和 home_id")
        result = controller.run_scene(scene_id, home_id)
        return success_response(**result)

    if action == "list_consumables":
        home_id = args.get("home_id")
        items = controller.list_consumables(home_id=home_id)
        return success_response(data=items)

    if action == "get_statistics":
        payload = args.get("payload") or {}
        data = controller.get_statistics(payload)
        return success_response(data=data)

    if action == "get_device_spec":
        model = args.get("model")
        if not model:
            raise ValueError("获取设备规格需要提供 model")
        info = controller.get_device_spec(model)
        return success_response(data=info)

    raise ValueError(f"未支持的 action: {action}")


def main() -> None:
    raw = sys.argv[1] if len(sys.argv) > 1 else "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}
    action = payload.get("action")
    if not action:
        print(json.dumps({"success": False, "error": "缺少 action 参数"}, ensure_ascii=False))
        return
    try:
        result = handle_action(action, payload)
    except Exception as exc:  # noqa: BLE001
        result = handle_exception(exc)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

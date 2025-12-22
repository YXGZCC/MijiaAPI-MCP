#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""米家 API 辅助工具，负责登录、缓存与常用操作封装。"""
from __future__ import annotations

import json
import logging
import os
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") else logging.WARNING,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

try:
    from mijiaAPI import (
        mijiaAPI,
        mijiaDevice,
        APIError,
        DeviceActionError,
        DeviceGetError,
        DeviceNotFoundError,
        DeviceSetError,
        GetDeviceInfoError,
        LoginError,
        MultipleDevicesFoundError,
        get_device_info,
    )

    MIJIA_API_AVAILABLE = True
except ImportError:
    # 允许在未安装 mijiaAPI 的环境下以模拟模式运行
    MIJIA_API_AVAILABLE = False
    mijiaAPI = object  # type: ignore
    mijiaDevice = object  # type: ignore
    APIError = DeviceActionError = DeviceGetError = DeviceNotFoundError = DeviceSetError = GetDeviceInfoError = LoginError = MultipleDevicesFoundError = Exception  # type: ignore

MOCK_DEVICES: List[Dict[str, Any]] = [
    {
        "did": "12345678",
        "name": "客厅空调",
        "model": "xiaomi.aircondition.v1",
        "room_name": "客厅",
        "home_id": "home_mock_1",
        "home_name": "我的家",
        "isOnline": True,
    },
    {
        "did": "23456789",
        "name": "卧室台灯",
        "model": "yeelink.light.lamp1",
        "room_name": "卧室",
        "home_id": "home_mock_1",
        "home_name": "我的家",
        "isOnline": True,
    },
    {
        "did": "34567890",
        "name": "书房空气净化器",
        "model": "zhimi.airpurifier.v6",
        "room_name": "书房",
        "home_id": "home_mock_1",
        "home_name": "我的家",
        "isOnline": False,
    },
]

MOCK_HOMES: List[Dict[str, Any]] = [
    {
        "id": "home_mock_1",
        "name": "我的家",
        "roomlist": [
            {"id": "room_mock_living", "name": "客厅"},
            {"id": "room_mock_bedroom", "name": "卧室"},
            {"id": "room_mock_study", "name": "书房"},
        ],
    }
]


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _resolve_auth_path(custom_path: Optional[str]) -> str:
    base_path = custom_path or os.getenv("MIJIA_AUTH_PATH")
    if base_path:
        path = Path(base_path).expanduser().resolve()
    else:
        path = (Path.home() / ".config" / "mijia-api" / "auth.json").resolve()
    if path.is_dir():
        path = path / "auth.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def _select_home_name(home_map: Dict[str, Dict[str, Any]], home_id: Optional[str]) -> Optional[str]:
    if home_id is None:
        return None
    home = home_map.get(str(home_id))
    if home:
        return home.get("name")
    return None


@dataclass
class DeviceIdentifier:
    did: Optional[str] = None
    name: Optional[str] = None


class MijiaController:
    """封装 mijiaAPI 调用、模拟数据与错误处理"""

    def __init__(
        self,
        auth_path: Optional[str] = None,
        use_mock: Optional[bool] = None,
        sleep_time: float = 0.5,
    ) -> None:
        self.use_mock = _to_bool(use_mock, default=os.getenv("MIJIA_USE_MOCK", "0") in {"1", "true", "yes"})
        self.auth_path = _resolve_auth_path(auth_path)
        self.sleep_time = sleep_time
        self._api: Optional[mijiaAPI] = None
        self._home_map: Optional[Dict[str, Dict[str, Any]]] = None

    # region 初始化
    def _ensure_api(self) -> mijiaAPI:
        if self.use_mock:
            logger.warning("当前处于 MOCK 模式，无法执行真实 API 调用")
            raise RuntimeError("当前处于 MOCK 模式，无法执行真实 API 调用")
        if not MIJIA_API_AVAILABLE:
            logger.error("未检测到 mijiaAPI 库")
            raise RuntimeError("未检测到 mijiaAPI，请先执行 pip install -r python_scripts/requirements.txt")
        if self._api is None:
            auth_file = Path(self.auth_path)
            if not auth_file.exists():
                logger.error(f"未找到米家认证文件: {self.auth_path}")
                raise RuntimeError(
                    "未找到米家认证文件，请先在终端执行 `python -m mijiaAPI -l` 扫码登录"
                )
            logger.info(f"正在使用认证文件: {self.auth_path}")
            api = mijiaAPI(self.auth_path)
            try:
                with redirect_stdout(sys.stderr):
                    api.login()
                logger.info("米家 API 登录成功")
            except LoginError as exc:  # type: ignore[arg-type]
                logger.error(f"米家登录失败: {exc}")
                raise RuntimeError("米家登录失败，请重新在终端扫码登录：python -m mijiaAPI -l") from exc
            self._api = api
        return self._api


    def _ensure_home_map(self) -> Dict[str, Dict[str, Any]]:
        if self.use_mock:
            return {home["id"]: home for home in MOCK_HOMES}
        if self._home_map is None:
            api = self._ensure_api()
            homes = api.get_homes_list()
            self._home_map = {str(home["id"]): home for home in homes}
        return self._home_map

    # endregion

    # region 数据访问
    def list_homes(self) -> List[Dict[str, Any]]:
        if self.use_mock:
            return MOCK_HOMES
        api = self._ensure_api()
        return api.get_homes_list()

    def list_devices(
        self,
        home_id: Optional[str] = None,
        include_shared: bool = False,
    ) -> List[Dict[str, Any]]:
        if self.use_mock:
            devices = MOCK_DEVICES
            if home_id:
                devices = [device for device in devices if device.get("home_id") == home_id]
            return devices

        api = self._ensure_api()
        devices = api.get_devices_list(home_id=home_id)
        if include_shared:
            devices.extend(api.get_shared_devices_list())

        home_map = self._ensure_home_map()
        for device in devices:
            device["home_name"] = _select_home_name(home_map, device.get("home_id"))
        return devices

    def list_shared_devices(self) -> List[Dict[str, Any]]:
        if self.use_mock:
            return []
        api = self._ensure_api()
        shared = api.get_shared_devices_list()
        for device in shared:
            device.setdefault("home_name", "shared")
        return shared

    def list_scenes(self, home_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            return [
                {
                    "scene_id": "scene_mock_goodnight",
                    "name": "晚安模式",
                    "home_id": "home_mock_1",
                }
            ]
        api = self._ensure_api()
        scenes = api.get_scenes_list(home_id=home_id)
        return scenes

    def run_scene(self, scene_id: str, home_id: str) -> Dict[str, Any]:
        if self.use_mock:
            return {"success": True, "message": f"Mock 场景 {scene_id} 已执行"}
        api = self._ensure_api()
        result = api.run_scene(scene_id, home_id)
        return {"success": True, "result": result}

    def list_consumables(self, home_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            return [
                {
                    "did": "34567890",
                    "device_name": "书房空气净化器",
                    "home_id": "home_mock_1",
                    "details": {
                        "description": "高效滤芯",
                        "value": "75%",
                    },
                }
            ]
        api = self._ensure_api()
        return api.get_consumable_items(home_id=home_id)

    def get_statistics(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        if self.use_mock:
            return [
                {"time": 1700000000, "value": 1.2},
                {"time": 1700003600, "value": 1.5},
            ]
        api = self._ensure_api()
        return api.get_statistics(payload)

    def get_device_spec(self, model: str) -> Dict[str, Any]:
        if self.use_mock:
            raise RuntimeError("MOCK 模式下不支持获取在线规格")
        cache_dir = Path(self.auth_path).with_name("spec_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        info = get_device_info(model, cache_path=cache_dir)
        return info

    # endregion

    # region 设备操作
    def _pick_device_record(
        self,
        identifier: DeviceIdentifier,
        include_shared: bool = True,
    ) -> Dict[str, Any]:
        devices = self.list_devices(include_shared=include_shared)
        if identifier.did:
            matches = [device for device in devices if str(device.get("did")) == str(identifier.did)]
        else:
            matches = [device for device in devices if device.get("name") == identifier.name]
        if not matches:
            raise DeviceNotFoundError(identifier.did or identifier.name or "unknown")
        if len(matches) > 1 and not identifier.did:
            raise MultipleDevicesFoundError(
                f"找到多个名称为 {identifier.name} 的设备，请提供 device_id"
            )
        return matches[0]

    def build_device_proxy(
        self,
        identifier: DeviceIdentifier,
        include_shared: bool = True,
    ) -> mijiaDevice:
        if self.use_mock:
            raise RuntimeError("MOCK 模式下不支持设备实时控制")
        api = self._ensure_api()
        kwargs: Dict[str, Optional[str]] = {
            "did": identifier.did,
            "dev_name": identifier.name,
        }
        return mijiaDevice(api, sleep_time=self.sleep_time, **kwargs)

    def get_device_status(
        self,
        identifier: DeviceIdentifier,
        properties: Optional[List[str]] = None,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        if self.use_mock:
            target = self._pick_device_record(identifier)
            return {
                "success": True,
                "device": target,
                "properties": {
                    "on": True,
                    "brightness": 60,
                },
                "note": "MOCK 数据，仅供演示",
            }

        device = self.build_device_proxy(identifier)
        response: Dict[str, Any] = {
            "success": True,
            "device": {
                "did": device.did,
                "name": device.name,
                "model": device.model,
            },
        }
        if properties:
            values = {}
            for prop in properties:
                values[prop] = device.get(prop)
            response["properties"] = values
        if include_metadata:
            response["available_properties"] = {
                name: {
                    "desc": prop.desc,
                    "rw": prop.rw,
                    "type": prop.type,
                    "unit": prop.unit,
                }
                for name, prop in device.prop_list.items()
                if "_" not in name or name.replace("_", "-") not in device.prop_list
            }
            response["available_actions"] = {
                name: {"desc": action.desc}
                for name, action in device.action_list.items()
            }
        return response

    def control_device(
        self,
        identifier: DeviceIdentifier,
        operation: str,
        prop_name: Optional[str] = None,
        value: Any = None,
        action_name: Optional[str] = None,
        action_value: Optional[Any] = None,
        action_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if self.use_mock:
            return {
                "success": True,
                "message": f"已在 MOCK 模式对 {identifier.name or identifier.did} 执行 {operation}",
            }
        device = self.build_device_proxy(identifier)
        if operation == "set_property":
            if not prop_name:
                raise ValueError("set_property 操作需要 prop_name")
            device.set(prop_name, value)
            return {
                "success": True,
                "message": f"{device.name} 的 {prop_name} 已设置为 {value}",
            }
        if operation == "run_action":
            if not action_name:
                raise ValueError("run_action 操作需要 action_name")
            kwargs = action_kwargs or {}
            if action_value is not None:
                device.run_action(action_name, value=action_value, **kwargs)
            else:
                device.run_action(action_name, **kwargs)
            return {
                "success": True,
                "message": f"{device.name} 已执行动作 {action_name}",
            }
        raise ValueError(f"不支持的操作类型: {operation}")

    # endregion


def build_controller(args: Dict[str, Any]) -> MijiaController:
    return MijiaController(
        auth_path=args.get("auth_path"),
        use_mock=args.get("use_mock"),
        sleep_time=float(args.get("sleep_time", 0.5)),
    )


def success_response(**kwargs: Any) -> Dict[str, Any]:
    return {"success": True, **kwargs}


def error_response(message: str, details: Optional[Any] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"success": False, "error": message}
    if details is not None:
        payload["details"] = details
    return payload


def handle_exception(exc: Exception) -> Dict[str, Any]:
    return error_response(str(exc))


__all__ = [
    "MijiaController",
    "DeviceIdentifier",
    "build_controller",
    "success_response",
    "error_response",
    "handle_exception",
]

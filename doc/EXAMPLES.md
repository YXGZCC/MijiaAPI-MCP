# 使用示例

本文档提供了 Mijia MCP Server 的实际使用示例，帮助您快速上手。

## 📚 目录

- [基础操作](#基础操作)
- [设备控制](#设备控制)
- [场景自动化](#场景自动化)
- [高级用法](#高级用法)

## 🎯 基础操作

### 1. 列出所有家庭

```json
{
  "tool": "list_mijia_homes",
  "arguments": {}
}
```

**返回示例**：
```json
{
  "success": true,
  "data": [
    {
      "id": "184001292211",
      "name": "我的家",
      "roomlist": [
        {"id": "room1", "name": "客厅"},
        {"id": "room2", "name": "卧室"}
      ]
    }
  ]
}
```

### 2. 获取设备列表

```json
{
  "tool": "get_mijia_devices",
  "arguments": {
    "home_id": "184001292211",
    "include_shared": false
  }
}
```

**返回示例**：
```json
{
  "success": true,
  "data": [
    {
      "did": "372745975",
      "name": "客厅摄像头",
      "model": "chuangmi.camera.ipc021",
      "isOnline": true,
      "localip": "172.22.22.108"
    }
  ]
}
```

## 🎮 设备控制

### 3. 查询设备状态

```json
{
  "tool": "get_device_status",
  "arguments": {
    "device_name": "客厅摄像头",
    "include_metadata": true
  }
}
```

**返回示例**：
```json
{
  "success": true,
  "device": {
    "did": "372745975",
    "name": "客厅摄像头",
    "model": "chuangmi.camera.ipc021"
  },
  "available_properties": {
    "on": {
      "desc": "Switch Status",
      "rw": "rw",
      "type": "bool"
    },
    "night-shot": {
      "desc": "Night Shot",
      "rw": "rw",
      "type": "uint"
    }
  },
  "available_actions": {
    "start-p2p-stream": {
      "desc": "Start P2P Stream"
    }
  }
}
```

### 4. 控制设备 - 开关

**打开摄像头**：
```json
{
  "tool": "control_device",
  "arguments": {
    "device_name": "客厅摄像头",
    "operation": "set_property",
    "prop_name": "on",
    "value": true
  }
}
```

**关闭摄像头**：
```json
{
  "tool": "control_device",
  "arguments": {
    "device_id": "372745975",
    "operation": "set_property",
    "prop_name": "on",
    "value": false
  }
}
```

### 5. 控制设备 - 调整属性

**设置台灯亮度**：
```json
{
  "tool": "control_device",
  "arguments": {
    "device_name": "卧室台灯",
    "operation": "set_property",
    "prop_name": "brightness",
    "value": 80
  }
}
```

**设置台灯色温**：
```json
{
  "tool": "control_device",
  "arguments": {
    "device_name": "卧室台灯",
    "operation": "set_property",
    "prop_name": "color-temperature",
    "value": 4500
  }
}
```

### 6. 执行设备动作

```json
{
  "tool": "control_device",
  "arguments": {
    "device_name": "扫地机器人",
    "operation": "run_action",
    "action_name": "start-sweep",
    "action_value": []
  }
}
```

## 🏠 场景自动化

### 7. 列出场景

```json
{
  "tool": "list_mijia_scenes",
  "arguments": {
    "home_id": "184001292211"
  }
}
```

**返回示例**：
```json
{
  "success": true,
  "data": [
    {
      "scene_id": "scene_001",
      "name": "回家模式",
      "home_id": "184001292211"
    },
    {
      "scene_id": "scene_002",
      "name": "离家模式",
      "home_id": "184001292211"
    }
  ]
}
```

### 8. 触发场景

```json
{
  "tool": "run_mijia_scene",
  "arguments": {
    "scene_id": "scene_001",
    "home_id": "184001292211"
  }
}
```

## 🔍 高级用法

### 9. 查询耗材状态

```json
{
  "tool": "list_mijia_consumables",
  "arguments": {
    "home_id": "184001292211"
  }
}
```

**返回示例**：
```json
{
  "success": true,
  "data": [
    {
      "did": "34567890",
      "device_name": "空气净化器",
      "details": {
        "description": "HEPA 滤芯",
        "value": "75%",
        "remaining_days": 45
      }
    }
  ]
}
```

### 10. 获取统计数据

**查询耗电量**：
```json
{
  "tool": "get_mijia_statistics",
  "arguments": {
    "payload": {
      "did": "device_id",
      "key": "power_consumption",
      "data_type": "hour",
      "time_start": 1700000000,
      "time_end": 1700086400,
      "limit": 100
    }
  }
}
```

### 11. 获取设备规格

```json
{
  "tool": "get_device_spec",
  "arguments": {
    "model": "yeelink.light.lamp4"
  }
}
```

**返回示例**：
```json
{
  "success": true,
  "data": {
    "type": "urn:miot-spec-v2:device:light:0000A001",
    "description": "智能灯泡",
    "services": [
      {
        "iid": 2,
        "type": "urn:miot-spec-v2:service:light:00007802",
        "properties": [
          {
            "iid": 1,
            "type": "urn:miot-spec-v2:property:on:00000006",
            "description": "开关",
            "format": "bool",
            "access": ["read", "write", "notify"]
          }
        ]
      }
    ]
  }
}
```

### 12. 系统信息

```json
{
  "tool": "get_system_info",
  "arguments": {}
}
```

**返回示例**：
```json
{
  "server": {
    "name": "mijia-mcp-server",
    "version": "2.0.0"
  },
  "runtime": {
    "timestamp": "2025-01-17T10:30:00.000Z",
    "platform": "win32",
    "nodeVersion": "v18.17.0",
    "architecture": "x64",
    "uptimeSeconds": 3600
  },
  "environment": {
    "pythonPath": "python",
    "scriptDir": "./adapter",
    "debugMode": false
  }
}
```

## 🧪 Mock 模式示例

在开发测试时，可以使用 Mock 模式：

```json
{
  "tool": "get_mijia_devices",
  "arguments": {
    "use_mock": true
  }
}
```

**Mock 返回示例**：
```json
{
  "success": true,
  "data": [
    {
      "did": "12345678",
      "name": "客厅空调",
      "model": "xiaomi.aircondition.v1",
      "isOnline": true
    },
    {
      "did": "23456789",
      "name": "卧室台灯",
      "model": "yeelink.light.lamp1",
      "isOnline": true
    }
  ]
}
```

## 💡 实用技巧

### 按设备名称查询（无需记住 device_id）

```json
{
  "tool": "control_device",
  "arguments": {
    "device_name": "客厅摄像头",
    "operation": "set_property",
    "prop_name": "on",
    "value": true
  }
}
```

### 批量操作（通过场景）

创建一个"回家模式"场景，包含多个设备操作：
- 打开客厅灯
- 关闭摄像头
- 启动空气净化器

然后一次性触发：
```json
{
  "tool": "run_mijia_scene",
  "arguments": {
    "scene_id": "scene_home",
    "home_id": "184001292211"
  }
}
```

### 错误处理

所有工具在失败时会返回：
```json
{
  "success": false,
  "error": "错误描述",
  "tool": "工具名称",
  "timestamp": "2025-01-17T10:30:00.000Z"
}
```

## 🔗 相关文档

- [完整工具列表](README.md#功能概览)
- [开发者指南](DEVELOPMENT.md)
- [安装配置](SETUP_GUIDE.md)

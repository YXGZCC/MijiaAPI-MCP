# 米家 MCP 服务器配置指南

本指南帮助你完成 **Node.js + Python** 混合架构的米家 MCP 服务器部署，并按官方示例代码提供扫码登录、设备控制、场景联动、统计查询等功能。

---

## 1. 环境要求

| 组件 | 版本 |
| --- | --- |
| Node.js | ≥ 18 |
| npm | 最新稳定版 |
| Python | ≥ 3.10（建议 3.11，对于 `mijiaAPI` 兼容性最好） |
| pip | 最新稳定版 |

> 推荐在虚拟环境（`python -m venv .venv`）中安装 Python 依赖。

### 安装依赖

```bash
# Node.js 依赖
npm install

# Python 依赖（需先激活虚拟环境）
pip install -r python_scripts/requirements.txt
```

`python_scripts/requirements.txt` 中已包含：
- `mijiaAPI`（源码安装）
- `requests`
- `pillow`
- `pycryptodome`
- `qrcode`
- `tzlocal`

---

## 2. 首次扫码登录（必做）

mijiaAPI 默认将认证信息保存在：
- macOS/Linux：`~/.config/mijia-api/auth.json`
- Windows：`%USERPROFILE%\.config\mijia-api\auth.json`

你可以在 `.env` 或 MCP 配置中通过 `MIJIA_AUTH_PATH` 自定义保存路径。

### 登录步骤

1. 安装依赖后，在终端执行：

   ```bash
   python -m mijiaAPI -l
   # 或
   mijiaAPI -l
   ```

2. 终端会显示 ASCII 二维码，并输出一个备用链接。
3. 打开米家 APP 扫描二维码，并确认授权。
4. 成功后 `auth.json` 将被创建，后续调用会自动刷新 Token（若 Token 失效，会提示重新登录）。

> **提示**：若计划在 MCP 运行过程中触发扫码，请确保终端窗口可见；脚本会将二维码输出重定向到 `stderr`，不会影响 JSON 通信。

---

## 3. MCP 服务器配置

`c:/Users/chenz/AppData/Local/CodeBuddyExtension/Cache/CodeBuddyIDE/CodeBuddy/mcp/settings.json`

```json
{
  "mcpServers": {
    "mijia-mcp-server": {
      "command": "node",
      "args": ["c:/Users/chenz/CodeBuddy/20251216173558/dist/index.js"],
      "type": "stdio",
      "env": {
        "PYTHON_PATH": "c:/Users/chenz/CodeBuddy/20251216173558/.venv/Scripts/python.exe",
        "PYTHON_SCRIPT_DIR": "c:/Users/chenz/CodeBuddy/20251216173558/python_scripts",
        "MIJIA_AUTH_PATH": "c:/Users/chenz/.config/mijia-api/auth.json",
        "MIJIA_USE_MOCK": "0"
      },
      "disabled": false
    }
  }
}
```

### 常用环境变量

| 变量 | 说明 |
| --- | --- |
| `PYTHON_PATH` | Python 解释器路径（支持虚拟环境） |
| `PYTHON_SCRIPT_DIR` | Python 脚本根目录 |
| `MIJIA_AUTH_PATH` | 认证文件保存路径 |
| `MIJIA_USE_MOCK` | 设为 `1` 可启用模拟数据 |

---

## 4. 工具与示例

| MCP 工具 | 对应 action | 说明 |
| --- | --- | --- |
| `list_mijia_homes` | `list_homes` | 返回家庭列表 |
| `get_mijia_devices` | `list_devices` | 支持 `home_id`、`include_shared` |
| `get_device_status` | `device_status` | 支持 `device_id` / `device_name`、`properties` |
| `control_device` | `control_device` | `operation=set_property/run_action` |
| `list_mijia_scenes` | `list_scenes` | 查看场景 |
| `run_mijia_scene` | `run_scene` | 触发场景，需要 `scene_id` + `home_id` |
| `list_mijia_consumables` | `list_consumables` | 查看耗材 |
| `get_mijia_statistics` | `get_statistics` | 直接透传 `api.get_statistics` 的参数 |
| `get_device_spec` | `get_device_spec` | 查询米家规格平台 |

### 示例：获取设备列表

```json
{
  "tool": "get_mijia_devices",
  "arguments": {
    "home_id": "123456789",
    "include_shared": true
  }
}
```

### 示例：调节台灯亮度

```json
{
  "tool": "control_device",
  "arguments": {
    "device_name": "卧室台灯",
    "operation": "set_property",
    "prop_name": "brightness",
    "value": 60
  }
}
```

### 示例：运行“晚安”场景

```json
{
  "tool": "run_mijia_scene",
  "arguments": {
    "scene_id": "123456",
    "home_id": "987654321"
  }
}
```

### 示例：查询统计数据

```json
{
  "tool": "get_mijia_statistics",
  "arguments": {
    "payload": {
      "did": "device_did",
      "key": "7.1",
      "data_type": "stat_day_v3",
      "limit": 7,
      "time_start": 1700000000,
      "time_end": 1700600000
    }
  }
}
```

---

## 5. Mock 模式

- 设置 `MIJIA_USE_MOCK=1` 或在调用工具时传入 `"use_mock": true`
- 返回内置的模拟家庭/设备/场景数据，适合本地调试或演示

---

## 6. 故障排查

| 问题 | 解决方案 |
| --- | --- |
| Python 无法导入 `mijiaAPI` | 确认已执行 `pip install -r python_scripts/requirements.txt`，或运行 `pip show mijiaAPI` |
| 登录时 JSON 解析失败 | 先在终端手动执行 `python -m mijiaAPI -l` 完成登录，或确保终端支持二维码输出 |
| 设备名称重复 | 在调用中改用 `device_id`，避免 `MultipleDevicesFoundError` |
| 场景执行失败 | 确保 `scene_id` 与 `home_id` 匹配，可先调用 `list_mijia_scenes` |
| 统计数据为空 | 检查 `payload` 中的 `key`、`data_type`、`time` 参数是否正确 |

---

## 7. 扩展流程

1. 在 `python_scripts/mijia_tool.py` 中新增 action
2. 在 `src/index.ts` 的 `TOOLS` 列表中注册 MCP 工具
3. 通过 `callMijiaAction("new_action", payload)` 调用
4. `npm run build` 重新构建

---

## 8. 参考链接

- [mijiaAPI GitHub](https://github.com/Do1e/mijia-api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [ascii 二维码终端字体建议](https://github.com/Do1e/mijia-api#readme)

祝你玩得开心，智能家居更智慧！

# My MCP Server · 米家智能控制

一个使用 TypeScript + Python 构建的 Model Context Protocol (MCP) 服务器，整合了 [mijiaAPI](https://github.com/Do1e/mijia-api) 提供的米家智能家居能力，支持扫码登录、设备列表、属性读取与设置、场景联动、耗材查询、统计数据等常见操作。

## ✨ 功能概览

| 工具 | 描述 |
| --- | --- |
| `list_mijia_homes` | 列出米家账号下的全部家庭 |
| `get_mijia_devices` | 根据家庭筛选设备，支持包含共享设备 |
| `get_device_status` | 查询设备属性，可返回可用属性/动作元数据 |
| `control_device` | 设置属性或执行动作（如开关、亮度、切换场景） |
| `list_mijia_scenes` | 查看家庭下的手动场景 |
| `run_mijia_scene` | 触发指定场景（如“回家”、“晚安”） |
| `list_mijia_consumables` | 查看耗材/配件使用情况（滤芯、电池等） |
| `get_mijia_statistics` | 获取耗电量等统计数据（小时/天/周/月） |
| `get_device_spec` | 在线查询设备规格（属性 siid/piid、动作等） |
| `get_system_info` | 查看 MCP 运行环境信息 |

> 每个工具都支持 `use_mock=true`，便于在没有真实账号时调试。

## 🧱 项目结构

```
my-mcp-server/
├── src/index.ts                  # MCP 主入口（TypeScript）
├── dist/index.js                 # 构建输出
├── python_scripts/
│   ├── mijia_helper.py           # 登录、缓存、API 封装
│   ├── mijia_tool.py             # action 路由脚本
│   ├── get_mijia_devices.py      # 兼容旧入口（委托给 mijia_tool ）
│   ├── get_device_status.py
│   ├── control_device.py
│   ├── requirements.txt          # Python 依赖
│   └── test_environment.py       # 环境检测脚本
├── README.md / SETUP_GUIDE.md    # 文档
└── ...
```

## 🚀 安装与构建

```bash
# 安装 Node 依赖
npm install

# 安装 Python 依赖（建议在虚拟环境中执行）
pip install -r python_scripts/requirements.txt

# 构建 TypeScript
npm run build
```

## 🔐 首次扫码登录（必做）

1. **准备终端**：确保终端可以正常显示 ANSI 字符（以便展示二维码）。
2. **执行登录命令**（选择任意一种）：

   ```bash
   # 方式一：使用 Python 模块
   python -m mijiaAPI -l

   # 方式二：使用 CLI 命令
   mijiaAPI -l
   ```

3. 终端会打印 ASCII 二维码，同时输出一个可访问的二维码链接。
4. 用米家 APP 扫描二维码并确认登录。
5. 认证信息会自动保存到 `~/.config/mijia-api/auth.json`（可通过 `MIJIA_AUTH_PATH` 修改）。
6. 之后调用 MCP 工具会自动复用 Token，除非 Token 过期。

> **提示**：若希望在项目目录下保存认证信息，可在 `.env` 中设置 `MIJIA_AUTH_PATH=./.mijia-api/auth.json`。

## ⚙️ MCP 配置示例

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
        "MIJIA_AUTH_PATH": "c:/Users/chenz/.config/mijia-api/auth.json"
      }
    }
  }
}
```

## 🛠️ 工具参数参考

### `get_mijia_devices`
- `home_id` (string, 可选)：指定家庭 ID
- `include_shared` (boolean, default `false`)
- `use_mock` (boolean, 可选)

### `get_device_status`
- `device_id` 或 `device_name`（至少一个）
- `properties` (string[])：需要读取的属性列表（如 `on`, `brightness`）
- `include_metadata` (boolean, default `true`)
- `sleep_time` (number)：读取间隔（秒）

### `control_device`
- `device_id` 或 `device_name`
- `operation`：`set_property` / `run_action`
- `prop_name` + `value`：用于 `set_property`
- `action_name` + `action_value`：用于 `run_action`
- `action_kwargs` / `params`：为动作提供额外参数

### `list_mijia_scenes`
- `home_id` (string, 可选)

### `run_mijia_scene`
- `scene_id` (string) — 来自 `list_mijia_scenes`
- `home_id` (string)

### `get_mijia_statistics`
- `payload`：与 `api.get_statistics` 一致，例如：

```json
{
  "payload": {
    "did": "device_did",
    "key": "7.1",
    "data_type": "stat_month_v3",
    "limit": 6,
    "time_start": 1700000000,
    "time_end": 1702592000
  }
}
```

### `get_device_spec`
- `model` (string)：如 `yeelink.light.lamp4`

> 其余工具参数可在 `src/index.ts` 中查看 JSON Schema。

## 🧩 调试与 Mock 模式

- 通过 `.env` 或 MCP 配置设置 `MIJIA_USE_MOCK=1`，即可在没有真实账号/设备时返回模拟数据。
- `python python_scripts/test_environment.py "{}"` 可检查 Python 依赖状态。

## 🧱 扩展开发

1. 在 `python_scripts/mijia_tool.py` 中增加新的 `action`
2. 在 `src/index.ts` 中为该 action 注册一个 MCP 工具
3. 运行 `npm run build`

## 📝 许可证

本项目采用 **GPL-3.0** 开源许可证。

⚠️ **重要提示**：GPL-3.0 是具有"强传染性"的 Copyleft 许可证。

- ✅ 您可以自由使用、修改和分发本项目
- ✅ 您可以将其用于商业目的
- ⚠️ 如果您在项目中使用、修改或分发本代码（包括作为库依赖），您的整个项目也必须以 GPL-3.0 或兼容许可证开源发布
- ⚠️ 您必须公开源代码并声明修改内容

详见 [LICENSE](./LICENSE) 文件。

# Mijia MCP Server · 米家智能控制

一个使用 TypeScript + Python 构建的 Model Context Protocol (MCP) 服务器，整合了 [mijiaAPI](https://github.com/Do1e/mijia-api) 提供的米家智能家居能力，支持扫码登录、设备列表、属性读取与设置、场景联动、耗材查询、统计数据等常见操作。

## ✨ 功能概览

| 工具 | 描述 |
| --- | --- |
| `list_mijia_homes` | 列出米家账号下的全部家庭 |
| `get_mijia_devices` | 根据家庭筛选设备，支持包含共享设备 |
| `get_device_status` | 查询设备属性，可返回可用属性/动作元数据 |
| `control_device` | 设置属性或执行动作（如开关、亮度、切换场景） |
| `list_mijia_scenes` | 查看家庭下的手动场景 |
| `run_mijia_scene` | 触发指定场景（如"回家"、"晚安"） |
| `list_mijia_consumables` | 查看耗材/配件使用情况（滤芯、电池等） |
| `get_mijia_statistics` | 获取耗电量等统计数据（小时/天/周/月） |
| `get_device_spec` | 在线查询设备规格（属性 siid/piid、动作等） |
| `get_system_info` | 查看 MCP 运行环境信息 |

> 每个工具都支持 `use_mock=true`，便于在没有真实账号时调试。

## 🧱 项目结构

```
mijia-mcp-server/
├── .github/
│   └── workflows/        # GitHub Actions 工作流
├── adapter/              # Python 适配器层
│   ├── __init__.py
│   ├── mijia_adapter.py  # 米家 API 封装与缓存
│   └── mijia_tool.py     # 工具路由脚本
├── config/               # 配置文件
│   ├── .env.example      # 环境变量示例
│   ├── mcp-config-example.json
│   └── requirements.txt  # Python 依赖
├── doc/                  # 文档目录
│   ├── README.md         # 完整文档
│   ├── SETUP_GUIDE.md    # 安装指南
│   └── TEST_REPORT.md    # 测试报告
├── mcp_server/           # MCP 服务器主代码
│   └── server.ts         # TypeScript 主入口
├── utils/                # 工具函数
│   └── test_environment.py
├── dist/                 # 构建输出
├── __init__.py           # 包初始化
├── package.json
├── tsconfig.json
└── LICENSE
```

## 🚀 快速开始

### 安装依赖

```bash
# 安装 Node.js 依赖
npm install

# 安装 Python 依赖
pip install -r config/requirements.txt

# 构建 TypeScript
npm run build
```

### 首次扫码登录

```bash
# 方式一：使用 Python 模块
python -m mijiaAPI -l

# 方式二：使用 CLI 命令
mijiaAPI -l
```

终端会打印二维码，用米家 APP 扫描并确认登录。认证信息会自动保存到 `~/.config/mijia-api/auth.json`。

### 配置 MCP 客户端

在 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "mijia-mcp-server": {
      "command": "node",
      "args": ["path/to/dist/server.js"],
      "type": "stdio",
      "env": {
        "PYTHON_PATH": "path/to/python",
        "PYTHON_SCRIPT_DIR": "path/to/adapter",
        "MIJIA_AUTH_PATH": "~/.config/mijia-api/auth.json"
      }
    }
  }
}
```

## 📖 详细文档

- [完整使用文档](doc/README.md)
- [安装配置指南](doc/SETUP_GUIDE.md)
- [测试报告](doc/TEST_REPORT.md)

## 🧩 Mock 模式

通过设置环境变量 `MIJIA_USE_MOCK=1` 或在工具调用时传入 `use_mock: true`，可在没有真实账号/设备时返回模拟数据，便于开发测试。

## 🛠️ 开发扩展

1. 在 `adapter/mijia_tool.py` 中增加新的 `action`
2. 在 `mcp_server/server.ts` 中为该 action 注册一个 MCP 工具
3. 运行 `npm run build`

## 📝 许可证

本项目采用 **GPL-3.0** 开源许可证。

⚠️ **重要提示**：GPL-3.0 是具有"强传染性"的 Copyleft 许可证。

- ✅ 您可以自由使用、修改和分发本项目
- ✅ 您可以将其用于商业目的
- ⚠️ 如果您在项目中使用、修改或分发本代码（包括作为库依赖），您的整个项目也必须以 GPL-3.0 或兼容许可证开源发布
- ⚠️ 您必须公开源代码并声明修改内容

详见 [LICENSE](./LICENSE) 文件。

## 🙏 致谢

- [Do1e/mijia-api](https://github.com/Do1e/mijia-api) - 核心米家 API 库
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP 协议规范

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

# 配置文件说明

## requirements.txt

Python 依赖列表，包含 `mijiaAPI` 等必需库。

安装方式：
```bash
pip install -r config/requirements.txt
```

## .env.example

环境变量配置示例，复制为 `.env` 使用：

```bash
cp config/.env.example .env
```

可配置项：
- `MIJIA_AUTH_PATH`: 米家认证文件路径（默认：`~/.config/mijia-api/auth.json`）
- `MIJIA_USE_MOCK`: 是否启用模拟模式（`0` 或 `1`）
- `PYTHON_PATH`: Python 解释器路径
- `PYTHON_SCRIPT_DIR`: Python 脚本目录

## mcp-config-example.json

MCP 客户端配置示例，需根据实际路径调整：

```json
{
  "mcpServers": {
    "mijia-mcp-server": {
      "command": "node",
      "args": ["path/to/dist/server.js"],
      "type": "stdio",
      "env": {
        "PYTHON_PATH": "python",
        "PYTHON_SCRIPT_DIR": "path/to/adapter",
        "MIJIA_AUTH_PATH": "~/.config/mijia-api/auth.json"
      }
    }
  }
}
```

将此配置添加到你的 MCP 客户端配置文件中（如 Claude Desktop 的 `settings.json`）。

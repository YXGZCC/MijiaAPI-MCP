# 开发者指南

本文档基于 [MCP 开发规范](../test-README.md) 编写，提供项目开发、调试和测试的最佳实践。

## 📚 目录

- [开发环境设置](#开发环境设置)
- [调试 MCP 服务器](#调试-mcp-服务器)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [常见问题](#常见问题)

## 🛠️ 开发环境设置

### 必要工具

- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **npm** >= 9.0.0
- **uv** (推荐用于 Python 项目管理)

### 初始化项目

```bash
# 克隆项目
git clone https://github.com/YXGZCC/MijiaAPI-MCP.git
cd MijiaAPI-MCP

# 安装 Node.js 依赖
npm install

# 创建 Python 虚拟环境
python -m venv .venv

# Windows 激活虚拟环境
.venv\Scripts\activate

# Linux/Mac 激活虚拟环境
source .venv/bin/activate

# 安装 Python 依赖
pip install -r config/requirements.txt

# 构建 TypeScript
npm run build
```

### 环境变量配置

创建 `.env` 文件（可选）：

```bash
# 调试模式
DEBUG=true

# Python 路径（如使用虚拟环境）
PYTHON_PATH=.venv/Scripts/python.exe

# Python 脚本目录
PYTHON_SCRIPT_DIR=./adapter

# 米家认证文件路径
MIJIA_AUTH_PATH=~/.config/mijia-api/auth.json

# Mock 模式（开发测试时使用）
MIJIA_USE_MOCK=0
```

## 🔍 调试 MCP 服务器

### 方法 1: 使用 MCP Inspector (推荐)

MCP Inspector 是官方提供的可视化调试工具，可以实时测试工具调用。

```bash
# 方式 1: 使用 npm 脚本
npm run inspector

# 方式 2: 使用 npx
npx @modelcontextprotocol/inspector node dist/server.js

# 方式 3: 使用 mcp dev (需要先安装 mcp CLI)
npm install -g mcp
mcp dev dist/server.js
```

访问 `http://localhost:5173`，点击 **Connect** 连接服务器，然后在 **Tools** 标签中测试各个工具。

#### 故障排除

如果遇到端口占用错误，参考：
- https://github.com/liaokongVFX/MCP-Chinese-Getting-Started-Guide/issues/6

### 方法 2: 使用 VSCode 调试

在 VSCode 中按 `F5` 或点击 **运行和调试**，选择以下配置之一：

1. **调试 MCP 服务器** - 直接调试服务器代码
2. **MCP Inspector 调试** - 在 Inspector 中调试

断点设置位置：
- `mcp_server/server.ts` - TypeScript 层逻辑
- `adapter/mijia_tool.py` - Python 业务逻辑

### 方法 3: 日志调试

启用调试日志：

```bash
# Windows
set DEBUG=true
node dist/server.js

# Linux/Mac
DEBUG=true node dist/server.js
```

日志会输出到 `stderr`，包含：
- 工具调用请求和响应
- Python 脚本执行时间
- 错误详情和堆栈

## 📝 代码规范

### TypeScript 代码风格

遵循项目的 `tsconfig.json` 配置：

```typescript
// ✅ 推荐
async function callMijiaAction(
  action: string,
  params: Record<string, unknown> = {}
): Promise<any> {
  debugLog(`执行米家操作: ${action}`);
  return callPythonScript("mijia_tool.py", { ...params, action });
}

// ❌ 不推荐
async function callMijiaAction(action, params) {
  return callPythonScript("mijia_tool.py", { ...params, action });
}
```

### Python 代码风格

遵循 PEP 8 规范：

```python
# ✅ 推荐
def handle_action(action: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """处理工具操作"""
    controller: MijiaController = build_controller(args)
    # ...
    
# ❌ 不推荐
def handle_action(action, args):
    controller = build_controller(args)
    # ...
```

### 添加新工具

1. **在 `adapter/mijia_tool.py` 中添加 action 处理**：

```python
def handle_action(action: str, args: Dict[str, Any]) -> Dict[str, Any]:
    # ... 现有代码 ...
    
    if action == "your_new_action":
        # 实现新功能
        result = controller.your_new_method(args)
        return success_response(data=result)
```

2. **在 `mcp_server/server.ts` 中注册 MCP 工具**：

```typescript
const TOOLS: Tool[] = [
  // ... 现有工具 ...
  {
    name: "your_new_tool",
    description: "描述你的新工具功能",
    inputSchema: {
      type: "object",
      properties: {
        param1: {
          type: "string",
          description: "参数说明",
        },
      },
      required: ["param1"],
    },
  },
];

// 在 CallToolRequestSchema 处理器中添加
case "your_new_tool":
  result = await callMijiaAction("your_new_action", toolArgs);
  break;
```

3. **重新构建并测试**：

```bash
npm run build
npm run inspector
```

## 🧪 测试指南

### 单元测试（Python）

```bash
# 测试 Python 适配器
python utils/test_adapter.py

# 测试环境配置
python utils/test_environment.py
```

### 集成测试（MCP 服务器）

```bash
# 使用 Node.js 测试脚本
node utils/test_server.mjs

# 使用 Inspector 手动测试
npm run inspector
```

### Mock 模式测试

在开发阶段，使用 Mock 模式避免真实 API 调用：

```bash
# 启用 Mock 模式
export MIJIA_USE_MOCK=1

# 或在工具调用时传入参数
{
  "use_mock": true
}
```

## ❓ 常见问题

### Q1: Python 脚本执行失败

**问题**: `Python 脚本执行失败 (mijia_tool.py)`

**解决方案**:
1. 确认 Python 路径正确：
   ```bash
   which python  # Linux/Mac
   where python  # Windows
   ```
2. 确认虚拟环境已激活
3. 确认依赖已安装：`pip list | grep mijiaAPI`

### Q2: 米家认证失败

**问题**: `未找到米家认证文件`

**解决方案**:
```bash
# 重新登录
python -m mijiaAPI -l

# 或指定认证文件路径
export MIJIA_AUTH_PATH=/path/to/auth.json
```

### Q3: MCP Inspector 无法连接

**问题**: Inspector 显示连接错误

**解决方案**:
1. 确认服务器已构建：`npm run build`
2. 检查端口占用：`netstat -ano | findstr :5173`
3. 查看服务器日志输出

### Q4: TypeScript 编译错误

**问题**: `tsc` 报类型错误

**解决方案**:
```bash
# 清理并重新构建
rm -rf dist node_modules
npm install
npm run build
```

## 📖 参考资源

- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [mijiaAPI 文档](https://github.com/Do1e/mijia-api)
- [MCP 中文入门指南](../test-README.md)

## 🤝 贡献代码

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

确保：
- 代码通过 linter 检查
- 添加必要的测试
- 更新相关文档

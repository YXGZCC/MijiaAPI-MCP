# 项目结构说明

## 目录结构

```
mijia-mcp-server/
├── .github/
│   └── workflows/           # GitHub Actions 工作流
│       ├── build.yml        # 构建和测试
│       └── release.yml      # 自动发布
│
├── adapter/                 # Python 适配器层
│   ├── __init__.py         # 包初始化
│   ├── mijia_adapter.py    # 米家 API 封装、登录、缓存管理
│   └── mijia_tool.py       # 工具路由，处理各种 action
│
├── config/                  # 配置文件目录
│   ├── .env.example        # 环境变量示例
│   ├── mcp-config-example.json  # MCP 客户端配置示例
│   ├── requirements.txt    # Python 依赖列表
│   └── README.md           # 配置说明文档
│
├── doc/                     # 文档目录
│   ├── README.md           # 完整使用文档
│   ├── SETUP_GUIDE.md      # 安装配置指南
│   ├── TEST_REPORT.md      # 测试报告
│   └── PROJECT_STRUCTURE.md # 本文件
│
├── mcp_server/              # MCP 服务器核心代码
│   └── server.ts           # TypeScript 主入口，处理 MCP 协议
│
├── utils/                   # 工具脚本
│   ├── __init__.py         # 包初始化
│   ├── test_environment.py # 环境检测脚本
│   ├── test_adapter.py     # 适配器测试
│   └── test_server.mjs     # MCP 服务器测试
│
├── dist/                    # TypeScript 构建输出（git ignore）
│   ├── server.js           # 编译后的服务器代码
│   └── server.d.ts         # 类型声明文件
│
├── __init__.py              # 项目包初始化
├── package.json             # Node.js 项目配置
├── tsconfig.json            # TypeScript 编译配置
├── pyproject.toml           # Python 项目配置（PEP 518）
├── setup.py                 # Python 安装脚本
├── MANIFEST.in              # Python 打包清单
├── release.py               # 发布辅助脚本
├── PUBLISH.md               # 发布指南
├── LICENSE                  # GPL-3.0 许可证
├── .gitignore               # Git 忽略规则
└── README.md                # 项目主文档
```

## 核心模块说明

### 1. MCP 服务器层 (`mcp_server/`)

**server.ts** - TypeScript 入口文件
- 实现 MCP 协议（Model Context Protocol）
- 定义所有可用工具及其 Schema
- 处理工具调用请求，转发给 Python 适配器
- 管理 stdio 传输通道

主要功能：
```typescript
- callPythonScript(): 执行 Python 脚本并解析 JSON 结果
- callMijiaAction(): 封装统一的 action 调用
- TOOLS[]: 定义 10 个 MCP 工具
- Server 初始化和请求处理
```

### 2. 适配器层 (`adapter/`)

**mijia_adapter.py** - 米家 API 适配器
- 封装 `mijiaAPI` 库的调用
- 处理登录、Token 缓存
- 提供 Mock 模式支持
- 统一错误处理和响应格式

主要类：
```python
- MijiaController: 控制器主类
  - list_homes(): 列出家庭
  - list_devices(): 列出设备
  - get_device_status(): 查询设备状态
  - control_device(): 控制设备
  - list_scenes(): 列出场景
  - ... 等
```

**mijia_tool.py** - 工具路由器
- 接收 TypeScript 传来的 action 和参数
- 路由到对应的 Controller 方法
- 返回 JSON 格式结果

支持的 actions：
```python
- list_homes
- list_devices
- device_status
- control_device
- list_scenes
- run_scene
- list_consumables
- get_statistics
- get_device_spec
```

### 3. 配置层 (`config/`)

**requirements.txt** - Python 依赖
```
mijiaAPI>=3.0.0
```

**.env.example** - 环境变量模板
```bash
MIJIA_AUTH_PATH=~/.config/mijia-api/auth.json
MIJIA_USE_MOCK=0
PYTHON_PATH=python
PYTHON_SCRIPT_DIR=./adapter
```

**mcp-config-example.json** - MCP 客户端配置示例

### 4. 工具层 (`utils/`)

**test_environment.py** - 检测 Python 环境和依赖

**test_adapter.py** - 测试适配器功能（Mock 模式）

**test_server.mjs** - 完整的 MCP 服务器集成测试

### 5. 文档层 (`doc/`)

- **README.md**: 完整功能文档
- **SETUP_GUIDE.md**: 详细安装指南
- **TEST_REPORT.md**: 测试用例和报告
- **PROJECT_STRUCTURE.md**: 本架构文档

## 数据流

```
MCP 客户端
    ↓
[MCP Protocol]
    ↓
mcp_server/server.ts
    ↓ (callPythonScript)
adapter/mijia_tool.py
    ↓ (handle_action)
adapter/mijia_adapter.py
    ↓ (MijiaController)
mijiaAPI 库
    ↓
米家云端 API
```

## 设计原则

1. **分层架构**: TypeScript MCP 层 + Python 适配器层，职责清晰
2. **依赖注入**: 通过环境变量配置路径，便于测试和部署
3. **Mock 支持**: 所有工具支持 Mock 模式，无需真实账号即可开发
4. **错误处理**: 统一的异常捕获和 JSON 错误响应
5. **可扩展性**: 新增工具只需在两层各添加一个函数即可

## 开发工作流

1. **新增功能**:
   - 在 `adapter/mijia_adapter.py` 添加方法
   - 在 `adapter/mijia_tool.py` 添加 action 路由
   - 在 `mcp_server/server.ts` 注册 MCP 工具
   - 更新文档

2. **测试**:
   ```bash
   # 测试适配器
   python utils/test_adapter.py
   
   # 测试 MCP 服务器
   node utils/test_server.mjs
   
   # 构建
   npm run build
   ```

3. **发布**:
   ```bash
   python release.py minor  # 或 major/patch
   git push origin main
   git push origin v2.1.0
   npm publish
   ```

## 依赖关系

```
Node.js >= 18.0.0
  └─ @modelcontextprotocol/sdk ^0.5.0
  └─ TypeScript ^5.9.3

Python >= 3.10
  └─ mijiaAPI >= 3.0.0
```

## 配置路径优先级

1. 环境变量 > 默认值
2. `PYTHON_SCRIPT_DIR`: 默认 `./adapter`
3. `MIJIA_AUTH_PATH`: 默认 `~/.config/mijia-api/auth.json`
4. `MIJIA_USE_MOCK`: 默认 `0`（关闭）

## 构建产物

```
dist/
├── server.js           # 主入口（可执行）
├── server.d.ts         # TypeScript 类型声明
├── server.js.map       # Source Map
└── server.d.ts.map     # 声明文件 Source Map
```

## 许可证

GPL-3.0 - 详见 [LICENSE](../LICENSE)

## 贡献指南

欢迎提交 Issue 和 Pull Request！请参考：
- [发布指南](../PUBLISH.md)
- [测试报告](TEST_REPORT.md)

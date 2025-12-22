#!/usr/bin/env node

import path from "node:path";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

const SERVER_NAME = "mijia-mcp-server";
const SERVER_VERSION = "2.0.0";

// 环境变量配置
const PYTHON_PATH = process.env.PYTHON_PATH || "python";
const PYTHON_SCRIPT_DIR = process.env.PYTHON_SCRIPT_DIR || "./adapter";
const DEBUG_MODE = process.env.DEBUG === "true" || process.env.DEBUG === "1";

// 日志工具
function log(level: "info" | "warn" | "error", ...args: any[]) {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
  console.error(prefix, ...args);
}

function debugLog(...args: any[]) {
  if (DEBUG_MODE) {
    log("info", "[DEBUG]", ...args);
  }
}

function resolveScriptPath(scriptName: string): string {
  const baseDir = path.isAbsolute(PYTHON_SCRIPT_DIR)
    ? PYTHON_SCRIPT_DIR
    : path.resolve(process.cwd(), PYTHON_SCRIPT_DIR);
  if (path.isAbsolute(scriptName)) {
    return scriptName;
  }
  return path.join(baseDir, scriptName);
}

/**
 * 调用 Python 脚本并返回 JSON 结果
 * @param scriptName Python 脚本名称
 * @param args 传递给脚本的参数对象
 * @returns 脚本执行结果（JSON 对象）
 */
async function callPythonScript(
  scriptName: string,
  args: Record<string, unknown> = {}
): Promise<any> {
  const startTime = Date.now();
  
  try {
    const scriptPath = resolveScriptPath(scriptName);
    const payload = JSON.stringify(args);
    
    debugLog(`调用 Python 脚本: ${scriptName}`, { args });
    
    const { stdout, stderr } = await execFileAsync(PYTHON_PATH, [scriptPath, payload], {
      env: process.env,
      timeout: 30000, // 30秒超时
    });

    if (stderr && stderr.trim()) {
      log("warn", `Python 脚本警告 (${scriptName}):`, stderr);
    }

    const output = (stdout ?? "").trim();
    if (!output) {
      throw new Error(`Python 脚本 ${scriptName} 未返回任何数据`);
    }
    
    const result = JSON.parse(output);
    const elapsed = Date.now() - startTime;
    debugLog(`Python 脚本执行成功: ${scriptName} (耗时: ${elapsed}ms)`);
    
    return result;

  } catch (error) {
    const elapsed = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : String(error);
    log("error", `Python 脚本执行失败 (${scriptName}, 耗时: ${elapsed}ms):`, errorMessage);
    throw new Error(`Python 脚本执行失败 (${scriptName}): ${errorMessage}`);
  }
}

/**
 * 调用米家 API 操作
 * @param action 操作类型
 * @param params 参数
 * @returns API 执行结果
 */
async function callMijiaAction(
  action: string,
  params: Record<string, unknown> = {}
): Promise<any> {
  debugLog(`执行米家操作: ${action}`);
  return callPythonScript("mijia_tool.py", { ...params, action });
}

/**
 * 将结果转换为 MCP 文本内容格式
 */
function asTextContent(result: unknown) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}

/**
 * 创建错误响应
 */
function createErrorResponse(error: unknown, toolName: string) {
  const message = error instanceof Error ? error.message : String(error);
  log("error", `工具执行失败 (${toolName}):`, message);
  
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify({
          success: false,
          error: message,
          tool: toolName,
          timestamp: new Date().toISOString(),
        }, null, 2),
      },
    ],
    isError: true,
  };
}

const TOOLS: Tool[] = [
  {
    name: "list_mijia_homes",
    description: "列出米家账号下的所有家庭（含共享家庭）",
    inputSchema: {
      type: "object",
      properties: {
        use_mock: {
          type: "boolean",
          description: "是否启用模拟数据模式",
        },
      },
    },
  },
  {
    name: "get_mijia_devices",
    description: "列出米家设备，可按家庭筛选并包含共享设备",
    inputSchema: {
      type: "object",
      properties: {
        home_id: {
          type: "string",
          description: "家庭 ID，可通过 list_mijia_homes 获取",
        },
        include_shared: {
          type: "boolean",
          description: "是否包含共享设备",
          default: false,
        },
        use_mock: {
          type: "boolean",
          description: "是否启用模拟数据模式",
        },
      },
    },
  },
  {
    name: "get_device_status",
    description: "获取设备属性并返回可用属性/动作列表",
    inputSchema: {
      type: "object",
      properties: {
        device_id: {
          type: "string",
          description: "设备 DID（优先使用）",
        },
        device_name: {
          type: "string",
          description: "设备名称（米家 APP 中的名称）",
        },
        properties: {
          type: "array",
          items: { type: "string" },
          description: "需要读取的属性名称数组，例如 on、brightness",
        },
        include_metadata: {
          type: "boolean",
          default: true,
          description: "是否返回属性/动作的元信息",
        },
        sleep_time: {
          type: "number",
          description: "读取属性之间的等待时间（秒）",
          default: 0.5,
        },
        use_mock: {
          type: "boolean",
        },
      },
      anyOf: [
        { required: ["device_id"] },
        { required: ["device_name"] },
      ],
    },
  },
  {
    name: "control_device",
    description: "设置属性或执行设备动作（如开关、亮度、run_action）",
    inputSchema: {
      type: "object",
      properties: {
        device_id: { type: "string" },
        device_name: { type: "string" },
        operation: {
          type: "string",
          enum: ["set_property", "run_action"],
          default: "set_property",
        },
        prop_name: {
          type: "string",
          description: "属性名称（set_property 时必填）",
        },
        value: {
          description: "属性值，可以是 number/string/bool",
        },
        action_name: {
          type: "string",
          description: "动作名称（run_action 时必填）",
        },
        action_value: {
          description: "动作参数 list，例如 [\"on\"]",
        },
        action_kwargs: {
          type: "object",
          description: "附加动作参数",
        },
        use_mock: {
          type: "boolean",
        },
      },
      anyOf: [
        { required: ["device_id"] },
        { required: ["device_name"] },
      ],
    },
  },
  {
    name: "list_mijia_scenes",
    description: "列出家庭下的米家手动场景",
    inputSchema: {
      type: "object",
      properties: {
        home_id: {
          type: "string",
          description: "家庭 ID，留空则列出所有家庭",
        },
        use_mock: {
          type: "boolean",
        },
      },
    },
  },
  {
    name: "run_mijia_scene",
    description: "执行指定家庭下的米家场景",
    inputSchema: {
      type: "object",
      properties: {
        scene_id: {
          type: "string",
          description: "场景 ID",
        },
        home_id: {
          type: "string",
          description: "家庭 ID",
        },
      },
      required: ["scene_id", "home_id"],
    },
  },
  {
    name: "list_mijia_consumables",
    description: "查询耗材/配件状态",
    inputSchema: {
      type: "object",
      properties: {
        home_id: {
          type: "string",
          description: "家庭 ID，留空则遍历所有家庭",
        },
        use_mock: {
          type: "boolean",
        },
      },
    },
  },
  {
    name: "get_mijia_statistics",
    description: "获取设备统计数据（耗电量等）",
    inputSchema: {
      type: "object",
      properties: {
        payload: {
          type: "object",
          description: "原始统计查询参数，需包含 did/key/data_type/time_start/time_end/limit",
        },
        use_mock: {
          type: "boolean",
        },
      },
      required: ["payload"],
    },
  },
  {
    name: "get_device_spec",
    description: "从米家规格平台获取设备属性/动作定义",
    inputSchema: {
      type: "object",
      properties: {
        model: {
          type: "string",
          description: "设备型号，例如 yeelink.light.lamp4",
        },
      },
      required: ["model"],
    },
  },
  {
    name: "get_system_info",
    description: "获取 MCP 服务器运行环境信息",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
];

const server = new Server(
  {
    name: SERVER_NAME,
    version: SERVER_VERSION,
  },
  {
    capabilities: { tools: {} },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const toolName = request.params.name;
  const toolArgs = (request.params.arguments ?? {}) as Record<string, unknown>;

  debugLog(`收到工具调用请求: ${toolName}`, toolArgs);

  try {
    let result: any;
    
    switch (toolName) {
      case "list_mijia_homes":
        result = await callMijiaAction("list_homes", toolArgs);
        break;
      case "get_mijia_devices":
        result = await callMijiaAction("list_devices", toolArgs);
        break;
      case "get_device_status":
        result = await callMijiaAction("device_status", toolArgs);
        break;
      case "control_device":
        result = await callMijiaAction("control_device", toolArgs);
        break;
      case "list_mijia_scenes":
        result = await callMijiaAction("list_scenes", toolArgs);
        break;
      case "run_mijia_scene":
        result = await callMijiaAction("run_scene", toolArgs);
        break;
      case "list_mijia_consumables":
        result = await callMijiaAction("list_consumables", toolArgs);
        break;
      case "get_mijia_statistics":
        result = await callMijiaAction("get_statistics", toolArgs);
        break;
      case "get_device_spec":
        result = await callMijiaAction("get_device_spec", toolArgs);
        break;
      case "get_system_info":
        result = {
          server: {
            name: SERVER_NAME,
            version: SERVER_VERSION,
          },
          runtime: {
            timestamp: new Date().toISOString(),
            platform: process.platform,
            nodeVersion: process.version,
            architecture: process.arch,
            uptimeSeconds: Math.floor(process.uptime()),
          },
          environment: {
            pythonPath: PYTHON_PATH,
            scriptDir: PYTHON_SCRIPT_DIR,
            debugMode: DEBUG_MODE,
          },
        };
        break;
      default:
        throw new Error(`未知的工具: ${toolName}`);
    }
    
    debugLog(`工具执行成功: ${toolName}`);
    return asTextContent(result);
    
  } catch (error) {
    return createErrorResponse(error, toolName);
  }
});

/**
 * MCP 服务器主入口函数
 */
async function main() {
  try {
    log("info", `正在启动 ${SERVER_NAME} v${SERVER_VERSION}...`);
    
    // 验证环境配置
    debugLog("环境配置:", {
      PYTHON_PATH,
      PYTHON_SCRIPT_DIR,
      DEBUG_MODE,
    });
    
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    log("info", `${SERVER_NAME} v${SERVER_VERSION} 已成功启动`);
    log("info", "等待客户端连接...");
    
  } catch (error) {
    log("error", "服务器启动失败:", error);
    process.exit(1);
  }
}

// 优雅退出处理
process.on("SIGINT", () => {
  log("info", "收到 SIGINT 信号，正在关闭服务器...");
  process.exit(0);
});

process.on("SIGTERM", () => {
  log("info", "收到 SIGTERM 信号，正在关闭服务器...");
  process.exit(0);
});

// 未捕获异常处理
process.on("uncaughtException", (error) => {
  log("error", "未捕获的异常:", error);
  process.exit(1);
});

process.on("unhandledRejection", (reason) => {
  log("error", "未处理的 Promise 拒绝:", reason);
  process.exit(1);
});

main().catch((error) => {
  log("error", "主程序异常:", error);
  process.exit(1);
});

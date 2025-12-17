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

const SERVER_NAME = "my-mcp-server";
const SERVER_VERSION = "1.1.0";

const PYTHON_PATH = process.env.PYTHON_PATH || "python";
const PYTHON_SCRIPT_DIR = process.env.PYTHON_SCRIPT_DIR || "./python_scripts";

function resolveScriptPath(scriptName: string): string {
  const baseDir = path.isAbsolute(PYTHON_SCRIPT_DIR)
    ? PYTHON_SCRIPT_DIR
    : path.resolve(process.cwd(), PYTHON_SCRIPT_DIR);
  if (path.isAbsolute(scriptName)) {
    return scriptName;
  }
  return path.join(baseDir, scriptName);
}

async function callPythonScript(
  scriptName: string,
  args: Record<string, unknown> = {}
): Promise<any> {
  try {
    const scriptPath = resolveScriptPath(scriptName);
    const payload = JSON.stringify(args);
    const { stdout, stderr } = await execFileAsync(PYTHON_PATH, [scriptPath, payload], {
      env: process.env,
    });

    if (stderr) {
      console.error(`[python:${scriptName}] ${stderr}`);
    }

    const output = (stdout ?? "").trim();
    if (!output) {
      throw new Error(`Python 脚本 ${scriptName} 未返回任何 JSON 数据`);
    }
    return JSON.parse(output);

  } catch (error) {
    throw new Error(`Python 脚本执行失败 (${scriptName}): ${error}`);
  }
}

async function callMijiaAction(
  action: string,
  params: Record<string, unknown> = {}
): Promise<any> {
  return callPythonScript("mijia_tool.py", { ...params, action });
}

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

  try {
    switch (toolName) {
      case "list_mijia_homes":
        return asTextContent(await callMijiaAction("list_homes", toolArgs));
      case "get_mijia_devices":
        return asTextContent(await callMijiaAction("list_devices", toolArgs));
      case "get_device_status":
        return asTextContent(await callMijiaAction("device_status", toolArgs));
      case "control_device":
        return asTextContent(await callMijiaAction("control_device", toolArgs));
      case "list_mijia_scenes":
        return asTextContent(await callMijiaAction("list_scenes", toolArgs));
      case "run_mijia_scene":
        return asTextContent(await callMijiaAction("run_scene", toolArgs));
      case "list_mijia_consumables":
        return asTextContent(await callMijiaAction("list_consumables", toolArgs));
      case "get_mijia_statistics":
        return asTextContent(await callMijiaAction("get_statistics", toolArgs));
      case "get_device_spec":
        return asTextContent(await callMijiaAction("get_device_spec", toolArgs));
      case "get_system_info": {
        const info = {
          timestamp: new Date().toISOString(),
          platform: process.platform,
          nodeVersion: process.version,
          architecture: process.arch,
          uptimeSeconds: process.uptime(),
        };
        return asTextContent(info);
      }
      default:
        throw new Error(`未知的工具: ${toolName}`);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text" as const,
          text: `错误: ${message}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`${SERVER_NAME} v${SERVER_VERSION} 已启动`);
}

main().catch((error) => {
  console.error("服务器启动失败:", error);
  process.exit(1);
});

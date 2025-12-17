import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function testServer() {
  console.log("🧪 测试 MCP 服务器...\n");
  
  const client = new Client(
    { name: "TestClient", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );

  const transport = new StdioClientTransport({
    command: "node",
    args: ["dist/server.js"],
  });

  try {
    await client.connect(transport);
    console.log("✓ 服务器连接成功\n");

    // 测试 list_tools
    const tools = await client.listTools({});
    console.log(`✓ 获取到 ${tools.tools.length} 个工具:`);
    tools.tools.forEach(tool => {
      console.log(`  - ${tool.name}: ${tool.description}`);
    });

    // 测试 Mock 模式
    console.log("\n🧪 测试 Mock 模式...\n");
    
    const homes = await client.callTool({
      name: "list_mijia_homes",
      arguments: { use_mock: true },
    });
    console.log("✓ list_mijia_homes:", JSON.stringify(homes, null, 2));

    const devices = await client.callTool({
      name: "get_mijia_devices",
      arguments: { use_mock: true },
    });
    console.log("\n✓ get_mijia_devices:", JSON.stringify(devices, null, 2));

    const systemInfo = await client.callTool({
      name: "get_system_info",
      arguments: {},
    });
    console.log("\n✓ get_system_info:", JSON.stringify(systemInfo, null, 2));

    await client.close();
    console.log("\n✅ 所有测试通过！");
    
  } catch (error) {
    console.error("\n❌ 测试失败:", error);
    process.exit(1);
  }
}

testServer();

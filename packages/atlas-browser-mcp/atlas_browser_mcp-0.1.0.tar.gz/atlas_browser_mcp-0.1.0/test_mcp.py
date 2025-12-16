"""最小 MCP server 測試"""

import asyncio
import sys

print("[TEST] Starting minimal MCP server...", file=sys.stderr)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("[TEST] MCP imports OK", file=sys.stderr)
except ImportError as e:
    print(f"[TEST] Import failed: {e}", file=sys.stderr)
    print("[TEST] Try: pip install mcp", file=sys.stderr)
    sys.exit(1)

server = Server("test-server")

@server.list_tools()
async def list_tools():
    print("[TEST] list_tools called", file=sys.stderr)
    return [
        Tool(
            name="hello",
            description="Says hello",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    print(f"[TEST] call_tool: {name}", file=sys.stderr)
    return [TextContent(type="text", text="Hello from test server!")]

async def run():
    print("[TEST] Starting server...", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        print("[TEST] stdio connected", file=sys.stderr)
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

def main():
    print("[TEST] main()", file=sys.stderr)
    asyncio.run(run())

if __name__ == "__main__":
    main()
"""
Atlas Browser MCP Server

Visual web browsing for AI agents via Model Context Protocol.
"""

import asyncio
import json
import sys
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

# 設置 logging（可選，輸出到 stderr）
logging.basicConfig(
    level=logging.WARNING,
    format='[atlas-browser] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# 創建 MCP server
server = Server("atlas-browser")

# === 延遲導入 browser ===
_browser = None


def get_browser():
    """延遲初始化瀏覽器實例"""
    global _browser
    if _browser is None:
        from .browser import VisualBrowser
        _browser = VisualBrowser(headless=False, humanize=True)
    return _browser


# === 工具定義 ===

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="navigate",
            description="Navigate to a URL and return a screenshot with labeled interactive elements",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="screenshot",
            description="Take a screenshot of the current page with labeled elements",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="click",
            description="Click on an element by its label ID (shown as [N] on the screenshot)",
            inputSchema={
                "type": "object",
                "properties": {
                    "label_id": {
                        "type": "integer",
                        "description": "The numeric label shown on the element (e.g., 5 for [5])"
                    }
                },
                "required": ["label_id"]
            }
        ),
        Tool(
            name="multi_click",
            description="Click multiple elements at once (useful for CAPTCHA, checkboxes, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "label_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of label IDs to click (e.g., [1, 5, 8])"
                    }
                },
                "required": ["label_ids"]
            }
        ),
        Tool(
            name="type",
            description="Type text at the current focus position",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    },
                    "submit": {
                        "type": "boolean",
                        "description": "Press Enter after typing (default: false)",
                        "default": False
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="scroll",
            description="Scroll the page up or down",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down"],
                        "description": "Scroll direction (default: down)",
                        "default": "down"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent]:
    """執行工具調用"""
    browser = get_browser()
    
    try:
        if name == "navigate":
            result = await asyncio.to_thread(
                browser.execute, 
                action="navigate", 
                url=arguments.get("url")
            )
        
        elif name == "screenshot":
            result = await asyncio.to_thread(
                browser.execute,
                action="observe"
            )
        
        elif name == "click":
            result = await asyncio.to_thread(
                browser.execute,
                action="click",
                label_id=arguments.get("label_id")
            )
        
        elif name == "multi_click":
            result = await asyncio.to_thread(
                browser.execute,
                action="multi_click",
                label_ids=arguments.get("label_ids")
            )
        
        elif name == "type":
            result = await asyncio.to_thread(
                browser.execute,
                action="type",
                text=arguments.get("text"),
                submit=arguments.get("submit", False)
            )
        
        elif name == "scroll":
            result = await asyncio.to_thread(
                browser.execute,
                action="scroll",
                direction=arguments.get("direction", "down")
            )
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return format_result(result)
        
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def format_result(result) -> list[TextContent | ImageContent]:
    """將 BrowserResult 轉換為 MCP 回應格式"""
    contents = []
    
    if not result.success:
        return [TextContent(type="text", text=f"Error: {result.error}")]
    
    data = result.data or {}
    
    # 如果有截圖，加入圖像
    if data.get("screenshot"):
        contents.append(ImageContent(
            type="image",
            data=data["screenshot"],
            mimeType="image/jpeg"
        ))
    
    # 構建文字資訊
    info = {
        "url": data.get("url", ""),
        "title": data.get("title", ""),
        "elements": data.get("elements", []),
        "element_count": data.get("element_count", 0)
    }
    
    # 如果是 multi_click，加入點擊結果
    if "clicks" in data:
        info["clicks"] = data["clicks"]
        info["clicked_count"] = data.get("clicked_count", 0)
    
    contents.append(TextContent(
        type="text",
        text=json.dumps(info, ensure_ascii=False)
    ))
    
    return contents


async def run():
    """運行 MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """程式入口點"""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hello-world-mcp")

# Create server instance
app = Server("hello-world-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_greeting",
            description="Returns a friendly greeting",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet"
                    }
                },
                "required": ["name"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "get_greeting":
        user_name = arguments.get("name", "Friend")
        greeting = f"Hello, {user_name}! 🎉 Your Python MCP server is working!"
        
        logger.info(f"Generated greeting for {user_name}")
        
        return [TextContent(
            type="text",
            text=greeting
        )]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server."""
    logger.info("Starting Hello World MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
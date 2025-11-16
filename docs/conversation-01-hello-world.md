# Conversation 1: MCP Foundation & Hello World Server

## 📚 What You Learned

In this conversation, we established the foundation for building MCP (Model Context Protocol) servers that extend Claude's capabilities. We created a simple "hello world" server to understand the architecture and get your development environment working.

## 🎯 Goals Achieved

- ✅ Understood MCP architecture and how it works
- ✅ Set up Python development environment
- ✅ Created first functional MCP server
- ✅ Configured Claude Desktop integration
- ✅ Tested the complete workflow

---

## 🏗️ Understanding MCP Architecture

### What is MCP?

**Model Context Protocol (MCP)** is Anthropic's standard for connecting Claude to external tools and data sources. Think of it as a universal "plugin system" for Claude.

### How It Works

```
┌─────────────────────────────────────────────────┐
│            Claude Desktop Application            │
│  (Your chat interface)                          │
└──────────────────┬──────────────────────────────┘
                   │
                   │ MCP Protocol (JSON-RPC)
                   │
┌──────────────────▼──────────────────────────────┐
│              MCP Server (Python)                 │
│  - Exposes tools to Claude                      │
│  - Receives requests from Claude                │
│  - Executes actions                             │
│  - Returns results                              │
└──────────────────┬──────────────────────────────┘
                   │
                   │ Your custom logic
                   │
┌──────────────────▼──────────────────────────────┐
│         External Systems/Data Sources            │
│  - Web scraping (Upwork)                        │
│  - APIs (Zoho CRM)                              │
│  - Databases                                    │
│  - File systems                                 │
└─────────────────────────────────────────────────┘
```

### Key Concepts

**Tools:** Functions that Claude can call (like `get_greeting`, `upwork_get_jobs`)

**Resources:** Data sources Claude can read (not used in our project)

**Prompts:** Pre-defined prompt templates (not used in our project)

**Communication:** Uses JSON-RPC over stdio (standard input/output)

---

## 🛠️ Step-by-Step Setup

### Step 1: Environment Setup

#### 1.1 Create Project Directory

```bash
# Create main project folder
mkdir upwork-zoho-automation
cd upwork-zoho-automation

# Create MCP servers directory
mkdir mcp-servers
cd mcp-servers

# Create hello-world test server
mkdir hello-world
cd hello-world
```

#### 1.2 Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Your prompt should now show (venv)
```

**Why virtual environments?**
- Isolates project dependencies
- Prevents version conflicts
- Makes project portable
- Each MCP server can have its own dependencies

#### 1.3 Install MCP SDK

```bash
pip install mcp
```

This installs the Anthropic MCP Python SDK which provides:
- Server class for creating MCP servers
- Decorators for registering tools
- Transport layer (stdio communication)
- Type definitions

---

### Step 2: Create Hello World Server

Create `server.py` in your `hello-world` folder:

```python
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

# Create an MCP server instance
# The name "hello-world" identifies this server
app = Server("hello-world")

# Define what tools are available
@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    This function tells Claude what tools this server provides.
    Claude Desktop calls this when it starts up.
    """
    return [
        Tool(
            name="get_greeting",
            description="Returns a friendly greeting with the person's name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the person to greet"
                    }
                },
                "required": ["name"]
            }
        )
    ]

# Handle tool calls from Claude
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    This function executes when Claude calls one of your tools.
    
    Args:
        name: The tool name (e.g., "get_greeting")
        arguments: Dictionary of arguments (e.g., {"name": "John"})
    
    Returns:
        List of TextContent with the result
    """
    if name == "get_greeting":
        person_name = arguments.get("name", "friend")
        greeting = f"Hello, {person_name}! Welcome to MCP servers!"
        
        return [TextContent(
            type="text",
            text=greeting
        )]
    
    # If unknown tool, raise error
    raise ValueError(f"Unknown tool: {name}")

# Main entry point
async def main():
    """
    Runs the MCP server using stdio transport.
    This connects the server to Claude Desktop.
    """
    from mcp.server.stdio import stdio_server
    
    # stdio_server handles communication with Claude Desktop
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

#### Code Explanation

**1. Server Creation:**
```python
app = Server("hello-world")
```
- Creates an MCP server instance
- The name identifies this server to Claude Desktop
- You can have multiple servers with different names

**2. Tool Registration:**
```python
@app.list_tools()
async def list_tools() -> list[Tool]:
```
- Decorator that registers this function
- Claude Desktop calls this on startup
- Returns list of available tools with descriptions
- The `inputSchema` uses JSON Schema to define parameters

**3. Tool Execution:**
```python
@app.call_tool()
async def call_tool(name: str, arguments: dict):
```
- Called when Claude invokes a tool
- Receives tool name and arguments
- Must return list of TextContent objects
- Can handle multiple tools with if/elif logic

**4. Communication Layer:**
```python
async with stdio_server() as (read_stream, write_stream):
```
- Sets up stdio (standard input/output) communication
- Claude Desktop writes requests to stdin
- Server writes responses to stdout
- All communication is JSON-RPC format

---

### Step 3: Test the Server Manually

Before integrating with Claude Desktop, verify the server works:

```bash
# Make sure venv is activated
python server.py
```

**What happens:**
- Server starts and waits for input
- It's listening on stdin (doesn't print anything yet)
- Press Ctrl+C to stop

This confirms Python can run your server without errors.

---

### Step 4: Configure Claude Desktop

#### 4.1 Locate Config File

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Full path example: `C:\Users\YourName\AppData\Roaming\Claude\claude_desktop_config.json`

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

#### 4.2 Edit Configuration

Open the file and add your MCP server:

```json
{
  "mcpServers": {
    "hello-world": {
      "command": "python",
      "args": [
        "C:\\Users\\YourName\\upwork-zoho-automation\\mcp-servers\\hello-world\\server.py"
      ]
    }
  }
}
```

**Important Notes:**

1. **Use FULL absolute paths** - Relative paths don't work
2. **Use double backslashes** on Windows (`\\`) or forward slashes (`/`)
3. **Don't use `~` or `%USERPROFILE%`** - Use actual path
4. **JSON syntax matters** - Watch commas and brackets
5. **The key** (`"hello-world"`) should match your server name

#### 4.3 Restart Claude Desktop

**Completely quit and restart:**
1. Close all Claude Desktop windows
2. Right-click system tray icon → Quit
3. Wait 5 seconds
4. Start Claude Desktop again

---

### Step 5: Test Integration

Once Claude Desktop restarts:

1. **Check for MCP indicator:**
   - Look for a 🔌 or tools icon in the chat interface
   - This indicates MCP servers are connected

2. **Try using the tool:**
   ```
   You: "Use the get_greeting tool with my name: John"
   ```

3. **Claude should respond:**
   ```
   I'll greet you using the hello-world server!
   [Calls get_greeting tool]
   
   Hello, John! Welcome to MCP servers!
   ```

---

## 🐛 Troubleshooting Guide

### Problem: Server Not Showing Up

**Check 1: Config File Syntax**
```bash
# Validate JSON syntax
python -m json.tool claude_desktop_config.json
```

**Check 2: Path Correctness**
- Open Windows Explorer
- Navigate to the path in your config
- Verify `server.py` exists there
- Copy the EXACT path from Explorer's address bar

**Check 3: Python in PATH**
```bash
# Verify Python is accessible
where python
```

**Check 4: Server Errors**
```bash
# Run server manually to see errors
cd path\to\hello-world
venv\Scripts\activate
python server.py
```

### Problem: Tool Not Working

**Check 1: Server Name Match**
- Ensure config key matches `Server("hello-world")`

**Check 2: Tool Name**
- Verify tool name in `list_tools()` matches what Claude calls

**Check 3: Virtual Environment**
- Config must use venv's Python if dependencies are installed there
- Example: `"C:\\...\\venv\\Scripts\\python.exe"`

### Problem: "Module not found: mcp"

**Solution:**
```bash
# Activate venv first
venv\Scripts\activate

# Then install
pip install mcp

# Verify installation
pip list | findstr mcp
```

---

## 🎓 Key Takeaways

### MCP Server Lifecycle

1. **Startup:**
   - Claude Desktop reads config file
   - Launches each MCP server as subprocess
   - Calls `list_tools()` to discover capabilities

2. **Tool Call:**
   - User asks Claude to do something
   - Claude recognizes it needs a tool
   - Sends JSON-RPC request to server
   - Server's `call_tool()` executes
   - Returns result to Claude
   - Claude incorporates result in response

3. **Shutdown:**
   - Claude Desktop closes
   - Sends shutdown signal to servers
   - Servers clean up and exit

### Best Practices Learned

1. **Always use virtual environments** - Keeps dependencies clean
2. **Test servers standalone first** - Easier debugging
3. **Use absolute paths** - Relative paths cause confusion
4. **Descriptive tool names** - Helps Claude choose correctly
5. **Good descriptions** - Claude reads these to decide when to use tools
6. **Error handling** - Return meaningful errors in `call_tool()`

---

## 📚 Code Structure Template

For future MCP servers, use this template:

```python
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

# 1. Create server
app = Server("server-name")

# 2. Register tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="tool_name",
            description="What this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "..."}
                },
                "required": ["param"]
            }
        )
    ]

# 3. Implement tool logic
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "tool_name":
        # Your logic here
        result = do_something(arguments["param"])
        return [TextContent(type="text", text=result)]
    
    raise ValueError(f"Unknown tool: {name}")

# 4. Run server
async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ➡️ Next Steps

With MCP fundamentals mastered, you're ready for **Conversation 2: Upwork Scraper**

We'll build a real-world MCP server that:
- Launches a headless browser
- Logs into Upwork
- Scrapes job listings
- Extracts structured data
- Returns it to Claude

The complexity increases, but the MCP structure remains the same!

---

## 📝 Files Created

```
upwork-zoho-automation/
└── mcp-servers/
    └── hello-world/
        ├── venv/              (virtual environment)
        └── server.py          (MCP server code)

%APPDATA%\Claude\
└── claude_desktop_config.json  (Claude configuration)
```

---

## 🔗 Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [JSON Schema Reference](https://json-schema.org/)
- [Anthropic Claude API Docs](https://docs.anthropic.com/)

---

**Congratulations!** 🎉 You've successfully created your first MCP server and integrated it with Claude Desktop. This foundation will support all future servers we build together.

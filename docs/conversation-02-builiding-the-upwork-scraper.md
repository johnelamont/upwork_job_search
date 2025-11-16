# Conversation 2: Building the Upwork Scraper MCP Server

Perfect! Let's build your Upwork scraper. I'll break this into clear sections with explanations so you understand how each piece works.

## 📋 Overview: What We're Building

**Architecture:**
```
Claude Desktop → MCP Server → Playwright Browser → Upwork
                     ↓
              Job Data Returns
```

**The MCP server will expose tools like:**
- `upwork_get_jobs` - Fetches recent job postings from your feed
- `upwork_get_job_details` - Gets full details for a specific job

**How it works:**
1. Playwright launches a real Chrome browser (headless)
2. It logs into Upwork using your credentials
3. Navigates to your job feed
4. Scrapes the HTML to extract job data
5. Returns structured data to Claude

---

## Step 1: Set Up the Project Structure

First, let's create a new directory for this MCP server:

```bash
# Create the directory
mkdir upwork_mcp_server
cd upwork_mcp_server

# Create Python virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows

# Install dependencies
pip install mcp playwright python-dotenv
playwright install chromium
```

**Why these packages?**
- `mcp` - The MCP SDK we used before
- `playwright` - Browser automation (like Selenium but better)
- `python-dotenv` - Securely store your Upwork credentials
- `chromium` - The actual browser Playwright will control

---

## Step 2: Create Environment File for Credentials

Create a file called `.env` in your `upwork_mcp_server` folder:

```
UPWORK_USERNAME=your_email@example.com
UPWORK_PASSWORD=your_password
```

**Security note:** Never commit this file to git! Add `.env` to `.gitignore` if you use version control.

---

## Step 3: Create the MCP Server File

Create `server.py`:

```python
import asyncio
import os
from mcp.server import Server
from mcp.types import Tool, TextContent
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Create MCP server instance
app = Server("upwork-scraper")

# Global browser context (we'll reuse it)
browser_context = None
page = None

async def init_browser():
    """Initialize the browser and login to Upwork"""
    global browser_context, page
    
    if browser_context is not None:
        return  # Already initialized
    
    playwright = await async_playwright().start()
    
    # Launch browser (headless=False for debugging, True for production)
    browser = await playwright.chromium.launch(headless=False)
    
    # Create a persistent context (keeps cookies/session)
    browser_context = await browser.new_context()
    page = await browser_context.new_page()
    
    # Login to Upwork
    await page.goto("https://www.upwork.com/ab/account-security/login")
    
    # Wait for and fill in login form
    await page.fill('input[id="login_username"]', os.getenv("UPWORK_USERNAME"))
    await page.click('button[id="login_password_continue"]')
    
    # Wait for password field and fill it
    await page.wait_for_selector('input[id="login_password"]')
    await page.fill('input[id="login_password"]', os.getenv("UPWORK_PASSWORD"))
    await page.click('button[id="login_control_continue"]')
    
    # Wait for login to complete (adjust selector based on Upwork's actual page)
    await page.wait_for_url("**/nx/find-work/**", timeout=30000)
    
    print("✅ Successfully logged into Upwork")

async def scrape_jobs():
    """Scrape job postings from Upwork feed"""
    global page
    
    await init_browser()
    
    # Navigate to the job feed
    await page.goto("https://www.upwork.com/nx/find-work/best-matches")
    
    # Wait for jobs to load
    await page.wait_for_selector('[data-test="job-tile-list"]', timeout=10000)
    
    # Extract job data using JavaScript in the browser
    jobs = await page.evaluate("""
        () => {
            const jobTiles = document.querySelectorAll('[data-test="JobTile"]');
            const jobs = [];
            
            jobTiles.forEach(tile => {
                try {
                    // Extract job details from the tile
                    const titleElement = tile.querySelector('[data-test="UpLink"]');
                    const title = titleElement ? titleElement.innerText : 'N/A';
                    const jobUrl = titleElement ? titleElement.href : '';
                    
                    // Extract job ID from URL (e.g., /jobs/~012345abcdef)
                    const jobIdMatch = jobUrl.match(/jobs\/(~[a-f0-9]+)/);
                    const jobId = jobIdMatch ? jobIdMatch[1] : 'N/A';
                    
                    const descElement = tile.querySelector('[data-test="job-description-text"]');
                    const description = descElement ? descElement.innerText : 'N/A';
                    
                    const budgetElement = tile.querySelector('[data-test="budget"]');
                    const budget = budgetElement ? budgetElement.innerText : 'N/A';
                    
                    const postedElement = tile.querySelector('[data-test="job-pubilshed-date"]');
                    const posted = postedElement ? postedElement.innerText : 'N/A';
                    
                    jobs.push({
                        jobId: jobId,
                        title: title,
                        description: description,
                        budget: budget,
                        posted: posted,
                        url: jobUrl
                    });
                } catch (e) {
                    console.error('Error parsing job tile:', e);
                }
            });
            
            return jobs;
        }
    """)
    
    return jobs

# Register the MCP tool
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="upwork_get_jobs",
            description="Fetches recent job postings from your Upwork feed. Returns job titles, descriptions, budgets, URLs, and unique job IDs.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "upwork_get_jobs":
        jobs = await scrape_jobs()
        
        return [TextContent(
            type="text",
            text=json.dumps(jobs, indent=2)
        )]
    
    raise ValueError(f"Unknown tool: {name}")

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

## 🔍 How This Code Works (Explained)

### **Browser Initialization (`init_browser`)**
- Creates a Playwright browser instance
- Opens Upwork's login page
- Fills in username/password from your `.env` file
- Waits for successful login (checks URL changes)
- Keeps the browser context alive for reuse

### **Job Scraping (`scrape_jobs`)**
- Navigates to your job feed
- Waits for jobs to load (using `data-test` attributes)
- Injects JavaScript into the page to extract data
- Returns structured JSON with job details

### **MCP Tool Registration**
- `@app.list_tools()` - Tells Claude what tools are available
- `@app.call_tool()` - Handles when Claude calls a tool
- Returns job data as JSON text

---

## Step 4: Test the Server Manually

Before integrating with Claude Desktop, let's test it:

```python
# Create test_scraper.py
import asyncio
from server import scrape_jobs, init_browser

async def test():
    await init_browser()
    jobs = await scrape_jobs()
    
    print(f"\n✅ Found {len(jobs)} jobs:\n")
    for job in jobs[:3]:  # Print first 3
        print(f"Title: {job['title']}")
        print(f"Job ID: {job['jobId']}")
        print(f"Budget: {job['budget']}")
        print(f"URL: {job['url']}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test())
```

Run it:
```bash
python test_scraper.py
```

**What to expect:**
- Browser window opens (because `headless=False`)
- Logs into Upwork
- Navigates to job feed
- Prints job details

**⚠️ Common Issues:**
1. **Selectors changed** - Upwork updates their HTML. You'll need to inspect the page and update selectors.
2. **Login fails** - Check credentials, or Upwork may require 2FA (we'll handle that next)
3. **Timeout errors** - Increase `timeout` values if your internet is slow

---

## Step 5: Configure Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hello-world": {
      "command": "python",
      "args": [
        "C:\\path\\to\\hello_world_server\\server.py"
      ]
    },
    "upwork-scraper": {
      "command": "python",
      "args": [
        "C:\\path\\to\\upwork_mcp_server\\server.py"
      ]
    }
  }
}
```

**Important:** Use full paths to `server.py`

---

## 🎯 What's Next?

After we get this working, here's what we'll add:

**Conversation 3: Zoho CRM Integration**
- Create MCP server for Zoho API
- Store jobs in CRM
- Check for duplicates using job ID

**Conversation 4: Job Evaluation Logic**
- Criteria matching
- Scoring system

**Conversation 5: Feedback Learning**
- Track your decisions
- Improve matching over time

---

## 📝 Your Action Items

1. **Set up the project structure** (folders, venv)
2. **Install dependencies** (mcp, playwright)
3. **Create `.env` file** with credentials
4. **Create `server.py`** with the code above
5. **Test manually** with `test_scraper.py`
6. **Update Claude Desktop config**

**Which step should we start with?** Or do you have questions about how any of this works before we begin?
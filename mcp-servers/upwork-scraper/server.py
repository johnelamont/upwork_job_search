import asyncio
import os
from pathlib import Path
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
playwright_instance = None

async def init_browser():
    """Initialize browser using your real Chrome profile"""
    global browser_context, page, playwright_instance
    
    if browser_context is not None:
        return  # Already initialized
    
    playwright_instance = await async_playwright().start()
    
    # Find your Chrome executable
    # Common locations on Windows:
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        raise Exception("Could not find Chrome installation. Please install Google Chrome.")
    
    # Your Chrome profile location
    user_data_dir = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    
    print(f"🌐 Launching your Chrome browser...")
    print(f"📁 Using profile from: {user_data_dir}")
    print("\n⚠️  IMPORTANT: Close ALL Chrome windows before continuing!")
    input("Press ENTER when all Chrome windows are closed: ")
    
    # Launch Chrome with your profile
    browser_context = await playwright_instance.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        executable_path=chrome_exe,
        headless=False,
        channel=None,  # Use the executable path instead of channel
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-first-run',
            '--no-default-browser-check'
        ],
        viewport={'width': 1920, 'height': 1080}
    )
    
    # Get or create page
    if len(browser_context.pages) > 0:
        page = browser_context.pages[0]
    else:
        page = await browser_context.new_page()
    
    # Navigate to Upwork job feed
    print("🔍 Navigating to Upwork job feed...")
    await page.goto("https://www.upwork.com/nx/find-work/best-matches", 
                    wait_until="domcontentloaded",
                    timeout=30000)
    
    await asyncio.sleep(3)
    
    current_url = page.url
    
    if "login" in current_url or "account-security" in current_url:
        print("\n" + "="*60)
        print("⚠️  Please log in manually in the browser window")
        print("="*60)
        input("Press ENTER when you see job listings: ")
    else:
        print("✅ Already logged in!")
    
    print(f"✅ Browser ready. Current URL: {page.url}")
async def scrape_jobs():
    """Scrape job postings from Upwork feed"""
    global page
    
    await init_browser()
    
    # Make sure we're on the job feed
    current_url = page.url
    if "find-work" not in current_url:
        print("🔄 Navigating to job feed...")
        await page.goto("https://www.upwork.com/nx/find-work/best-matches", 
                       wait_until="domcontentloaded",
                       timeout=30000)
        await asyncio.sleep(3)
    else:
        print("✅ Already on job feed")
        await asyncio.sleep(2)  # Brief wait for any dynamic content
    
    # Try to find job tiles
    try:
        await page.wait_for_selector('[data-test="JobTile"]', timeout=10000)
        print("✅ Job tiles found!")
    except Exception as e:
        print(f"⚠️  Could not find job tiles: {e}")
        print(f"Current URL: {page.url}")
        print("The page might not have loaded properly or selectors changed.")
    
    # Extract job data
    jobs = await page.evaluate(r"""
        () => {
            const jobTiles = document.querySelectorAll('[data-test="JobTile"]');
            const jobs = [];
            
            console.log('Found', jobTiles.length, 'job tiles');
            
            jobTiles.forEach(tile => {
                try {
                    const titleElement = tile.querySelector('[data-test="UpLink"]');
                    const title = titleElement ? titleElement.innerText : 'N/A';
                    const jobUrl = titleElement ? titleElement.href : '';
                    
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
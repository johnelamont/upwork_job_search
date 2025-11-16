import asyncio
import os
from mcp.server import Server
from mcp.types import Tool, TextContent
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json

load_dotenv()

app = Server("upwork-scraper")

browser_context = None
page = None

async def init_browser():
    """Connect to manually opened Chrome browser"""
    global browser_context, page
    
    if browser_context is not None:
        return
    
    print("\n" + "="*70)
    print("📋 MANUAL SETUP REQUIRED")
    print("="*70)
    print("\n1. Open Google Chrome normally (not through this script)")
    print("2. Log into Upwork")
    print("3. Navigate to: https://www.upwork.com/nx/find-work/best-matches")
    print("4. Make sure you can see your job listings")
    print("5. KEEP THAT CHROME WINDOW OPEN")
    print("\n6. Then open a NEW Command Prompt and run:")
    print('   chrome.exe --remote-debugging-port=9222')
    print("\n   Full command:")
    print('   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
    print("\n7. This will open a NEW Chrome window - log into Upwork in THIS window")
    print("="*70 + "\n")
    
    input("Press ENTER when you have Chrome running with --remote-debugging-port=9222 and you're logged into Upwork: ")
    
    playwright_instance = await async_playwright().start()
    
    try:
        # Connect to the existing Chrome instance
        browser = await playwright_instance.chromium.connect_over_cdp("http://localhost:9222")
        browser_context = browser.contexts[0]
        page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
        
        print(f"✅ Connected to Chrome! Current URL: {page.url}")
        
        # Navigate if not already on job feed
        if "find-work" not in page.url:
            await page.goto("https://www.upwork.com/nx/find-work/best-matches")
            await asyncio.sleep(2)
            
    except Exception as e:
        print(f"❌ Failed to connect to Chrome: {e}")
        print("\nMake sure you:")
        print("1. Closed all Chrome windows")
        print("2. Started Chrome with: chrome.exe --remote-debugging-port=9222")
        raise

async def scrape_jobs():
    """Scrape job postings"""
    global page
    
    await init_browser()
    
    # Make sure on job feed
    if "find-work" not in page.url:
        await page.goto("https://www.upwork.com/nx/find-work/best-matches")
        await asyncio.sleep(3)
    
    # Extract jobs
    jobs = await page.evaluate(r"""
        () => {
            const jobTiles = document.querySelectorAll('[data-test="JobTile"]');
            const jobs = [];
            
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
                    console.error('Error:', e);
                }
            });
            
            return jobs;
        }
    """)
    
    return jobs

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="upwork_get_jobs",
            description="Fetches recent job postings from your Upwork feed.",
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
        return [TextContent(type="text", text=json.dumps(jobs, indent=2))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
from playwright.async_api import async_playwright
import json

async def manual_scrape():
    """Simple scraper that you control entirely"""
    
    async with async_playwright() as p:
        # Launch a regular browser
        print("🚀 Launching browser...")
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("🌐 Navigating to Upwork...")
        try:
            await page.goto("https://www.upwork.com/ab/account-security/login", timeout=30000)
        except Exception as e:
            print(f"⚠️  Could not load login page automatically: {e}")
            print("Browser is open - please navigate to Upwork manually")
        
        print("\n" + "="*60)
        print("⚠️  MANUAL LOGIN")
        print("="*60)
        print("\nPlease do the following in the browser:")
        print("1. Complete login (solve Cloudflare if needed)")
        print("2. Navigate to your job feed at:")
        print("   https://www.upwork.com/nx/find-work/best-matches")
        print("3. Make sure jobs are visible on screen")
        print("\nWhen ready to scrape, press ENTER here...")
        print("="*60 + "\n")
        
        input("Press ENTER when you're logged in and see job listings: ")
        
        # Get current URL
        current_url = page.url
        print(f"\n📍 Current page: {current_url}")
        
        # If not on job feed, try to navigate there
        if "find-work" not in current_url:
            print("🔄 Attempting to navigate to job feed...")
            try:
                await page.goto("https://www.upwork.com/nx/find-work/best-matches", timeout=15000)
                await asyncio.sleep(3)
            except Exception as e:
                print(f"⚠️  Navigation failed: {e}")
                print("Continuing with current page...")
        
        # Try to extract jobs
        print("🔍 Attempting to extract jobs...")
        
        jobs = await page.evaluate(r"""
            () => {
                // Try multiple possible selectors
                let jobTiles = document.querySelectorAll('[data-test="JobTile"]');
                
                if (jobTiles.length === 0) {
                    jobTiles = document.querySelectorAll('article');
                }
                
                const jobs = [];
                
                console.log('Found ' + jobTiles.length + ' potential job elements');
                
                jobTiles.forEach(tile => {
                    try {
                        // Try to find title with various selectors
                        let titleElement = tile.querySelector('[data-test="UpLink"]') || 
                                         tile.querySelector('h2 a') || 
                                         tile.querySelector('h3 a') ||
                                         tile.querySelector('a[href*="/jobs/"]');
                        
                        if (!titleElement) return;
                        
                        const title = titleElement.innerText || titleElement.textContent || 'N/A';
                        const jobUrl = titleElement.href || '';
                        
                        // Extract job ID
                        const jobIdMatch = jobUrl.match(/jobs\/(~[a-f0-9]+)/);
                        const jobId = jobIdMatch ? jobIdMatch[1] : 'N/A';
                        
                        // Try to find description
                        let descElement = tile.querySelector('[data-test="job-description-text"]') ||
                                        tile.querySelector('[data-test="Description"]') ||
                                        tile.querySelector('p');
                        const description = descElement ? (descElement.innerText || descElement.textContent) : 'N/A';
                        
                        // Try to find budget
                        let budgetElement = tile.querySelector('[data-test="budget"]') ||
                                          tile.querySelector('[data-test="Budget"]');
                        const budget = budgetElement ? budgetElement.innerText : 'N/A';
                        
                        // Try to find posted date
                        let postedElement = tile.querySelector('[data-test="job-pubilshed-date"]') ||
                                          tile.querySelector('[data-test="PostedOn"]') ||
                                          tile.querySelector('small');
                        const posted = postedElement ? postedElement.innerText : 'N/A';
                        
                        if (jobId !== 'N/A') {
                            jobs.push({
                                jobId: jobId,
                                title: title.trim(),
                                description: description.trim().substring(0, 200) + '...',
                                budget: budget.trim(),
                                posted: posted.trim(),
                                url: jobUrl
                            });
                        }
                    } catch (e) {
                        console.error('Error parsing job:', e);
                    }
                });
                
                return jobs;
            }
        """)
        
        print(f"\n✅ Extracted {len(jobs)} jobs!\n")
        
        if len(jobs) > 0:
            for i, job in enumerate(jobs[:5], 1):
                print(f"\n--- Job {i} ---")
                print(f"Title: {job['title']}")
                print(f"Job ID: {job['jobId']}")
                print(f"Budget: {job['budget']}")
                print(f"Posted: {job['posted']}")
                print(f"URL: {job['url'][:80]}...")
                print("-" * 60)
            
            # Save to file
            with open('scraped_jobs.json', 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2)
            print(f"\n💾 All {len(jobs)} jobs saved to scraped_jobs.json")
        else:
            print("\n⚠️  No jobs found. Taking screenshots for debugging...")
            
            await page.screenshot(path='debug_screenshot.png', full_page=True)
            print("📸 Screenshot saved to debug_screenshot.png")
            
            # Save page HTML for inspection
            html = await page.content()
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("📄 Page HTML saved to debug_page.html")
            print("\nPlease share these files so we can fix the selectors!")
        
        print("\n🔍 Keeping browser open for 30 seconds...")
        await asyncio.sleep(30)
        
        await browser.close()
        print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(manual_scrape())
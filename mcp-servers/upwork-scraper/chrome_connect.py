import asyncio
from playwright.async_api import async_playwright
import json

async def connect_to_chrome():
    """Connect to your manually-opened Chrome"""
    
    async with async_playwright() as p:
        print("🔌 Connecting to your Chrome browser...")
        
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            contexts = browser.contexts
            if not contexts:
                print("❌ No browser contexts found.")
                return
            
            context = contexts[0]
            pages = context.pages
            
            if not pages:
                print("❌ No pages open.")
                return
                
            page = pages[0]
            
            print(f"✅ Connected! Current URL: {page.url}")
            
            # Navigate to job feed if not there
            if "find-work" not in page.url:
                print("🔄 Navigating to job feed...")
                await page.goto("https://www.upwork.com/nx/find-work/best-matches")
                await asyncio.sleep(3)
            
            print("🔍 Scraping jobs...")
            
            # Updated selectors based on the actual HTML structure
            jobs = await page.evaluate(r"""
                () => {
                    // Find all job tile sections - using the correct selector
                    const jobSections = document.querySelectorAll('section[data-ev-label="visible_job_tile_impression"]');
                    const jobs = [];
                    
                    console.log('Found ' + jobSections.length + ' job sections');
                    
                    jobSections.forEach(section => {
                        try {
                            // Get the job title and link
                            const titleElement = section.querySelector('h3.job-tile-title a');
                            if (!titleElement) return;
                            
                            const title = titleElement.innerText.trim();
                            const jobUrl = titleElement.href;
                            
                            // Extract job ID from URL (format: /jobs/Title_~021989444526465937858/)
                            const jobIdMatch = jobUrl.match(/_(~0\d+)/);
                            const jobId = jobIdMatch ? jobIdMatch[1] : 'N/A';
                            
                            // Get description - look for description text
                            const descElement = section.querySelector('[data-test="UpCLineClamp"] span');
                            const description = descElement ? descElement.innerText.trim() : 'N/A';
                            
                            // Get budget - look for budget section
                            const budgetSection = section.querySelector('ul li strong[data-test]');
                            const budget = budgetSection ? budgetSection.innerText.trim() : 'N/A';
                            
                            // Get posted date
                            const postedElement = section.querySelector('[data-test="posted-on"]');
                            const posted = postedElement ? postedElement.innerText.trim() : 'N/A';
                            
                            // Get client info
                            const clientSpent = section.querySelector('strong[data-test="client-spend"]');
                            const clientSpentText = clientSpent ? clientSpent.innerText.trim() : 'N/A';
                            
                            const clientCountry = section.querySelector('[data-test="client-country"]');
                            const country = clientCountry ? clientCountry.innerText.trim() : 'N/A';
                            
                            const proposals = section.querySelector('[data-test="proposals"]');
                            const proposalsText = proposals ? proposals.innerText.trim() : 'N/A';
                            
                            jobs.push({
                                jobId: jobId,
                                title: title,
                                description: description,
                                budget: budget,
                                posted: posted,
                                clientSpent: clientSpentText,
                                clientCountry: country,
                                proposals: proposalsText,
                                url: jobUrl
                            });
                        } catch (e) {
                            console.error('Error parsing job:', e);
                        }
                    });
                    
                    return jobs;
                }
            """)
            
            print(f"\n✅ Found {len(jobs)} jobs!")
            
            if len(jobs) > 0:
                # Save to file
                with open('scraped_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(jobs, f, indent=2)
                
                # Display first 5 jobs
                for i, job in enumerate(jobs[:5], 1):
                    print(f"\n{'='*70}")
                    print(f"Job {i}: {job['title']}")
                    print(f"{'='*70}")
                    print(f"Job ID: {job['jobId']}")
                    print(f"Budget: {job['budget']}")
                    print(f"Posted: {job['posted']}")
                    print(f"Client Spent: {job['clientSpent']}")
                    print(f"Country: {job['clientCountry']}")
                    print(f"Proposals: {job['proposals']}")
                    print(f"Description: {job['description'][:150]}...")
                    print(f"URL: {job['url']}")
                
                if len(jobs) > 5:
                    print(f"\n... and {len(jobs) - 5} more jobs")
                
                print(f"\n💾 All {len(jobs)} jobs saved to scraped_jobs.json")
            else:
                print("⚠️  No jobs found. Make sure you're on the job feed page.")
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(connect_to_chrome())
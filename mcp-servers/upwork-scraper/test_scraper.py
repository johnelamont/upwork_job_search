import asyncio
from server import scrape_jobs, init_browser

async def test():
    print("🚀 Starting browser and login process...\n")
    await init_browser()
    
    print("\n🔍 Now scraping jobs...")
    jobs = await scrape_jobs()
    
    print(f"\n✅ Found {len(jobs)} jobs:\n")
    
    if len(jobs) == 0:
        print("⚠️  No jobs found! This might mean:")
        print("   - The page selectors need updating")
        print("   - The page didn't fully load")
        print("   - Your feed is empty")
    else:
        for i, job in enumerate(jobs[:5], 1):  # Print first 5
            print(f"\n--- Job {i} ---")
            print(f"Title: {job['title']}")
            print(f"Job ID: {job['jobId']}")
            print(f"Budget: {job['budget']}")
            print(f"Posted: {job['posted']}")
            print(f"URL: {job['url'][:80]}...")  # Truncate long URLs
            print("-" * 60)
    
    print(f"\n📊 Total jobs scraped: {len(jobs)}")
    print("\n✅ Test complete! Browser will stay open for 10 seconds...")
    await asyncio.sleep(10)  # Keep browser open briefly

if __name__ == "__main__":
    asyncio.run(test())
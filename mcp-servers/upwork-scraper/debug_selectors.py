import asyncio
from playwright.async_api import async_playwright
import json

async def debug_page():
    """Debug script to find the correct selectors"""
    
    async with async_playwright() as p:
        print("🔌 Connecting to Chrome...")
        
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            
            current_url = page.url
            print(f"📍 Current URL: {current_url}\n")
            
            # Take screenshot
            await page.screenshot(path='current_page.png', full_page=True)
            print("📸 Screenshot saved to current_page.png")
            
            # Save HTML
            html = await page.content()
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("📄 HTML saved to page_source.html")
            
            # Try to find various elements
            print("\n🔍 Looking for job-related elements...\n")
            
            # Check for different possible selectors
            selectors_to_try = [
                '[data-test="JobTile"]',
                '[data-test="job-tile"]',
                'article',
                '[class*="job"]',
                '[class*="Job"]',
                'section[class*="job"]',
                'div[class*="card"]',
                '[data-qa="job"]'
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                except:
                    pass
            
            # Get all elements with data-test attributes
            print("\n📋 All data-test attributes on page:")
            data_tests = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('[data-test]');
                    const tests = new Set();
                    elements.forEach(el => {
                        tests.add(el.getAttribute('data-test'));
                    });
                    return Array.from(tests).sort();
                }
            """)
            
            for test in data_tests[:20]:  # Show first 20
                print(f"  - {test}")
            
            if len(data_tests) > 20:
                print(f"  ... and {len(data_tests) - 20} more")
            
            # Try to extract ANY job-like content
            print("\n🔍 Attempting to extract any job content...\n")
            
            job_info = await page.evaluate("""
                () => {
                    // Look for any links that contain 'jobs' in the URL
                    const jobLinks = Array.from(document.querySelectorAll('a[href*="/jobs/"]'));
                    
                    return jobLinks.slice(0, 5).map(link => ({
                        text: link.innerText.trim().substring(0, 100),
                        href: link.href,
                        parentClass: link.parentElement?.className || 'N/A'
                    }));
                }
            """)
            
            if job_info and len(job_info) > 0:
                print("Found job links:")
                for i, job in enumerate(job_info, 1):
                    print(f"\n{i}. {job['text']}")
                    print(f"   URL: {job['href']}")
                    print(f"   Parent class: {job['parentClass'][:80]}")
            else:
                print("❌ No job links found")
            
            print("\n" + "="*60)
            print("📝 NEXT STEPS:")
            print("="*60)
            print("1. Open 'page_source.html' in a text editor")
            print("2. Search for text from a job title you can see on screen")
            print("3. Look at the HTML structure around that text")
            print("4. Find the data-test or class attributes used")
            print("5. Share those with me so I can update the selectors")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_page())
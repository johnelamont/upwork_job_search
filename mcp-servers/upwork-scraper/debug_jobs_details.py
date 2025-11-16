import asyncio
from playwright.async_api import async_playwright
import json

async def debug_job_details():
    """Debug script to explore job detail page structure"""
    
    async with async_playwright() as p:
        print("🔌 Connecting to your Chrome browser...")
        
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            
            current_url = page.url
            print(f"📍 Current URL: {current_url}\n")
            
            # Check if we're on a job detail page
            if "/jobs/" not in current_url:
                print("⚠️  You're not on a job detail page yet.")
                print("\nOptions:")
                print("1. Manually click on a job in your Chrome window")
                print("2. Or paste a job URL here\n")
                
                choice = input("Enter job URL (or press ENTER to wait for you to click a job): ").strip()
                
                if choice:
                    print(f"🔄 Navigating to {choice}...")
                    await page.goto(choice)
                    await asyncio.sleep(3)
                else:
                    print("\n⏳ Waiting for you to click on a job...")
                    print("Click a job in Chrome, then press ENTER here...")
                    input()
            
            current_url = page.url
            print(f"\n✅ Analyzing job page: {current_url}\n")
            
            # Take screenshot
            await page.screenshot(path='job_detail_page.png', full_page=True)
            print("📸 Full page screenshot saved to job_detail_page.png")
            
            # Save HTML
            html = await page.content()
            with open('job_detail_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("📄 HTML saved to job_detail_page.html")
            
            # Extract all data-test attributes
            print("\n" + "="*70)
            print("📋 ALL data-test ATTRIBUTES ON THIS PAGE")
            print("="*70)
            
            data_tests = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('[data-test]');
                    const tests = [];
                    elements.forEach(el => {
                        const attr = el.getAttribute('data-test');
                        const text = el.innerText ? el.innerText.trim().substring(0, 60) : '';
                        tests.push({
                            attr: attr,
                            text: text,
                            tag: el.tagName.toLowerCase()
                        });
                    });
                    return tests;
                }
            """)
            
            # Group by attribute name
            attr_groups = {}
            for item in data_tests:
                attr = item['attr']
                if attr not in attr_groups:
                    attr_groups[attr] = []
                attr_groups[attr].append(item)
            
            for attr in sorted(attr_groups.keys()):
                items = attr_groups[attr]
                print(f"\n[data-test=\"{attr}\"] - Found {len(items)} element(s)")
                for item in items[:2]:  # Show first 2 examples
                    if item['text']:
                        print(f"  → {item['tag']}: \"{item['text']}\"")
                if len(items) > 2:
                    print(f"  ... and {len(items) - 2} more")
            
            # Extract potential field names
            print("\n" + "="*70)
            print("🔍 POTENTIAL JOB FIELDS (based on common patterns)")
            print("="*70)
            
            job_fields = await page.evaluate(r"""
                () => {
                    const fields = {};
                    
                    // Try to find common job detail fields
                    const selectors = {
                        'Job Title': [
                            'h1', 
                            'h2',
                            '[data-test*="title"]',
                            '[data-test*="Title"]'
                        ],
                        'Description': [
                            '[data-test*="description"]',
                            '[data-test*="Description"]',
                            '[class*="description"]'
                        ],
                        'Budget/Rate': [
                            '[data-test*="budget"]',
                            '[data-test*="Budget"]',
                            '[data-test*="rate"]',
                            '[data-test*="price"]'
                        ],
                        'Skills': [
                            '[data-test*="skill"]',
                            '[data-test*="Skill"]',
                            '[data-test*="tag"]'
                        ],
                        'Duration': [
                            '[data-test*="duration"]',
                            '[data-test*="Duration"]',
                            '[data-test*="length"]'
                        ],
                        'Experience Level': [
                            '[data-test*="experience"]',
                            '[data-test*="Experience"]',
                            '[data-test*="level"]'
                        ],
                        'Project Type': [
                            '[data-test*="type"]',
                            '[data-test*="Type"]',
                            '[data-test*="contract"]'
                        ],
                        'Client Info': [
                            '[data-test*="client"]',
                            '[data-test*="Client"]'
                        ],
                        'Posted Date': [
                            '[data-test*="posted"]',
                            '[data-test*="Posted"]',
                            '[data-test*="date"]'
                        ],
                        'Location': [
                            '[data-test*="location"]',
                            '[data-test*="Location"]',
                            '[data-test*="country"]'
                        ]
                    };
                    
                    for (const [fieldName, selectorList] of Object.entries(selectors)) {
                        for (const selector of selectorList) {
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > 0) {
                                const samples = [];
                                elements.forEach((el, idx) => {
                                    if (idx < 3) {  // First 3 examples
                                        const text = el.innerText || el.textContent || '';
                                        if (text.trim()) {
                                            samples.push({
                                                selector: selector,
                                                text: text.trim().substring(0, 100),
                                                tag: el.tagName.toLowerCase()
                                            });
                                        }
                                    }
                                });
                                if (samples.length > 0) {
                                    if (!fields[fieldName]) fields[fieldName] = [];
                                    fields[fieldName] = fields[fieldName].concat(samples);
                                }
                            }
                        }
                    }
                    
                    return fields;
                }
            """)
            
            for field_name, samples in job_fields.items():
                if samples:
                    print(f"\n{field_name}:")
                    seen = set()
                    for sample in samples[:3]:  # Show first 3 unique
                        key = (sample['selector'], sample['text'][:50])
                        if key not in seen:
                            seen.add(key)
                            print(f"  [{sample['selector']}]")
                            print(f"  → {sample['text']}")
            
            # Create a summary JSON
            summary = {
                'url': current_url,
                'total_data_test_attrs': len(attr_groups),
                'data_test_list': list(attr_groups.keys()),
                'potential_fields': job_fields
            }
            
            with open('job_detail_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            print("\n" + "="*70)
            print("💾 FILES CREATED:")
            print("="*70)
            print("1. job_detail_page.png - Screenshot of the page")
            print("2. job_detail_page.html - Full HTML source")
            print("3. job_detail_analysis.json - Structured analysis")
            print("\n" + "="*70)
            print("📝 NEXT STEPS:")
            print("="*70)
            print("1. Review the output above")
            print("2. Open the screenshot to see what fields you want")
            print("3. Tell me which fields to extract, and I'll create the scraper")
            print("="*70)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_job_details())
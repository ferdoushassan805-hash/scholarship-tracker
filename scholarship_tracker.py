import asyncio
import json
import os
from datetime import datetime, date
from playwright.async_api import async_playwright

# --- DETAILED SCHOLARSHIP KNOWLEDGE BASE ---
SCHOLARSHIP_DB = [
    {
        "name": "Chevening (UK)",
        "url": "https://www.chevening.org/scholarships/guidance/application-timeline/",
        "open_date": "2025-08-05",
        "deadline": "2025-10-07",
        "status_keyword": "Applications open at 12:00 UTC",
        "description": "Full funding for 1-year Master's in the UK."
    },
    {
        "name": "Fulbright Foreign Student (USA)",
        "url": "https://foreign.fulbrightonline.org/about/foreign-student-program",
        "open_date": "2026-02-01",
        "deadline": "2026-05-31",
        "status_keyword": "Competition is open",
        "description": "Master's and PhD funding for study in the USA."
    },
    {
        "name": "Turkiye Burslari (Turkey)",
        "url": "https://www.turkiyeburslari.gov.tr/calendar",
        "open_date": "2025-01-10",
        "deadline": "2025-02-20",
        "status_keyword": "Application Period",
        "description": "Undergraduate, Master's, and PhD in Turkey."
    },
    {
        "name": "Australia Awards",
        "url": "https://www.dfat.gov.au/people-to-people/australia-awards/australia-awards-scholarships",
        "open_date": "2026-02-01",
        "deadline": "2026-04-30",
        "status_keyword": "Opening date: 1 February",
        "description": "Focuses on Indo-Pacific regional development."
    },
    {
        "name": "Global Korea Scholarship (GKS)",
        "url": "https://www.studyinkorea.go.kr",
        "open_date": "2025-02-07",
        "deadline": "2025-03-03",
        "status_keyword": "GKS Notice",
        "description": "Fully funded degrees in South Korea."
    },
    {
        "name": "Erasmus Mundus (EU)",
        "url": "https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en",
        "open_date": "2025-10-01",
        "deadline": "2026-01-15",
        "status_keyword": "apply between October and January",
        "description": "Joint Master's degrees across multiple EU countries."
    },
    {
        "name": "MEXT (Japan)",
        "url": "https://www.studyinjapan.go.jp/en/smap-stopj-applications-research.html",
        "open_date": "2025-04-01",
        "deadline": "2025-05-24",
        "status_keyword": "Accepting Applications",
        "description": "Research, Undergraduate, and Tech college in Japan."
    }
]

DATA_FILE = "scholarship_master_list.json"

async def check_scholarships():
    print(f"--- Deep Search Monitor Started: {datetime.now().strftime('%Y-%m-%d')} ---\n")
    
    results = {}
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        
        # 1. SET AGENT: Applying custom User-Agent to mimic a real browser
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()

        for scholarship in SCHOLARSHIP_DB:
            name = scholarship["name"]
            print(f"📡 Scanning {name}...")
            
            try:
                # 2. LONGER TIMEOUT: Set to 90,000ms (90 seconds) for slow government portals
                await page.goto(scholarship["url"], timeout=90000, wait_until="domcontentloaded")
                
                # Extract content
                content = await page.content()
                
                # Identify if portal is LIVE right now
                is_live = scholarship["status_keyword"].lower() in content.lower()
                status = "🟢 OPEN" if is_live else "🔴 CLOSED"

                # Date Comparison Logic
                today = date.today()
                deadline = datetime.strptime(scholarship["deadline"], "%Y-%m-%d").date()
                open_date = datetime.strptime(scholarship["open_date"], "%Y-%m-%d").date()
                
                days_until_deadline = (deadline - today).days
                days_until_open = (open_date - today).days

                # Decision Engine
                alert = ""
                if is_live:
                    alert = f"🔥 ACTION REQUIRED: The {name} portal is active!"
                elif 0 < days_until_open <= 14:
                    alert = f"⏳ GET READY: {name} opens in {days_until_open} days."
                elif 0 < days_until_deadline <= 30:
                    alert = f"⚠️ DEADLINE WARNING: {name} closes in {days_until_deadline} days!"

                print(f"   Status: {status}")
                print(f"   Official Deadline: {scholarship['deadline']}")
                if alert:
                    print(f"   📢 {alert}")
                print("-" * 30)

                results[name] = {
                    "status": status,
                    "deadline": scholarship["deadline"],
                    "alert": alert,
                    "description": scholarship["description"],
                    "url": scholarship["url"],
                    "last_updated": datetime.now().isoformat()
                }

            except Exception as e:
                print(f"   ❌ Could not reach {name} within 90s. (Site may be down or blocking bot traffic)")

        await browser.close()

    # Save data for app use
    with open(DATA_FILE, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n✅ All checks complete. Data saved to {DATA_FILE}")

if __name__ == "__main__":
    asyncio.run(check_scholarships())
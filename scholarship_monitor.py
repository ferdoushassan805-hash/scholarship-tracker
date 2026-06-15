import asyncio
import json
import os
from datetime import datetime, date
from playwright.async_api import async_playwright

# --- UPDATED BANGLADESH-CENTRIC KNOWLEDGE BASE ---
SCHOLARSHIP_DB = [
    {
        "name": "Chevening (UK) - Bangladesh",
        "url": "https://www.chevening.org/scholarship/bangladesh/",
        "open_date": "2025-08-01",
        "deadline": "2025-11-01",
        "status_keyword": "Applications are open",
        "description": "Full funding for Masters in the UK for Bangladeshi professionals."
    },
    {
        "name": "Fulbright (USA) - Bangladesh",
        "url": "https://bd.usembassy.gov/fulbright-foreign-student-program-announcement/",
        "open_date": "2025-02-15",
        "deadline": "2025-05-15",
        "status_keyword": "is now accepting applications",
        "description": "Masters degree funding for Bangladeshi students in the USA."
    },
    {
        "name": "Turkiye Burslari (Turkey)",
        "url": "https://www.turkiyeburslari.gov.tr/calendar",
        "open_date": "2025-01-10",
        "deadline": "2025-02-25",
        "status_keyword": "Application Period",
        "description": "Full scholarship for UG, Masters, and PhD in Turkey."
    },
    {
        "name": "Australia Awards - Bangladesh",
        "url": "https://australiaawardsbangladesh.org/",
        "open_date": "2025-02-01",
        "deadline": "2025-04-30",
        "status_keyword": "Apply Now",
        "description": "Masters funding focused on Bangladesh's development sectors."
    },
    {
        "name": "Erasmus Mundus (EU)",
        "url": "https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en",
        "open_date": "2024-10-01",
        "deadline": "2025-01-31",
        "status_keyword": "applications are open",
        "description": "Joint Masters degrees across Europe for BD students."
    },
    {
        "name": "MEXT (Japan) - Bangladesh",
        "url": "https://www.bd.emb-japan.go.jp/itpr_en/scholarshipnotice.html",
        "open_date": "2025-04-15",
        "deadline": "2025-05-30",
        "status_keyword": "is now open",
        "description": "Full funding for research and degrees from the Govt of Japan."
    }
]

DATA_FILE = "scholarship_master_list.json"

async def check_scholarships():
    print(f"--- BD Scholarship Monitor Started: {datetime.now().strftime('%Y-%m-%d')} ---\n")
    results = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        for scholarship in SCHOLARSHIP_DB:
            name = scholarship["name"]
            print(f"📡 Checking {name}...")
            
            try:
                # 90 second timeout for potentially slow government sites
                await page.goto(scholarship["url"], timeout=90000, wait_until="domcontentloaded")
                content = await page.content()
                
                # Check live status
                is_live = scholarship["status_keyword"].lower() in content.lower()
                status = "🟢 OPEN" if is_live else "🔴 CLOSED"

                # Logic for dates
                today = date.today()
                deadline = datetime.strptime(scholarship["deadline"], "%Y-%m-%d").date()
                open_date = datetime.strptime(scholarship["open_date"], "%Y-%m-%d").date()
                
                days_to_deadline = (deadline - today).days
                days_to_open = (open_date - today).days

                alert = ""
                if is_live:
                    alert = f"🔥 APPLY NOW: The portal for {name} is active!"
                elif 0 < days_to_open <= 14:
                    alert = f"⏳ COMING SOON: {name} opens in {days_to_open} days."
                elif 0 < days_to_deadline <= 21:
                    alert = f"⚠️ HURRY: {name} closes in {days_to_deadline} days!"

                print(f"   Status: {status} | Info: {alert if alert else 'Tracking...'}")

                results[name] = {
                    "status": status,
                    "deadline": scholarship["deadline"],
                    "alert": alert,
                    "url": scholarship["url"],
                    "description": scholarship["description"],
                    "last_updated": datetime.now().isoformat()
                }

            except Exception as e:
                print(f"   ❌ Failed to load {name}. (Skipping)")

        await browser.close()

    with open(DATA_FILE, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n✅ Scan Complete. {DATA_FILE} updated.")

if __name__ == "__main__":
    asyncio.run(check_scholarships())
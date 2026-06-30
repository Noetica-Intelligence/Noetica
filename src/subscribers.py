"""
Scientific Intelligence Engine — Subscriber Management
Reads user preferences from a Google Sheet (Published to the Web as CSV).
"""

import os
import csv
import urllib.request
import urllib.error

def get_subscribers() -> list[dict]:
    """
    Fetch subscribers from Google Sheets.
    The sheet must be published to the web as a CSV.
    Expected columns: Timestamp, Email, Name, Expertise Level, Reading Time, 
                      Report Frequency, Interests, Discovery Preferences, 
                      Exploration Preference, Consent
    """
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("⚠️  No GOOGLE_SHEET_ID found. Defaulting to environment variable subscribers.")
        
        # Check NOETICA_SUBSCRIBERS first (comma separated list)
        subs_env = os.environ.get("NOETICA_SUBSCRIBERS")
        if subs_env:
            subs_list = []
            for email in subs_env.split(","):
                subs_list.append({
                    "Email": email.strip(),
                    "Name": email.split("@")[0].capitalize(),
                    "Reading Time": "15 Minutes",
                    "Interests": "All",
                    "Exploration Preference": "Yes",
                    "Report Frequency": "Daily"
                })
            return subs_list
            
        recipient = os.environ.get("RECIPIENT_EMAIL")
        if not recipient:
            return []
        return [{
            "Email": recipient,
            "Name": "Admin",
            "Reading Time": "15 Minutes",
            "Interests": "All",
            "Exploration Preference": "Yes",
            "Report Frequency": "Daily"
        }]

    # Fetch CSV from Google Sheets
    if sheet_id.startswith("http"):
        csv_url = sheet_id
    else:
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
    print(f"📥 Fetching subscribers from Google Sheet...")
    
    try:
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            lines = [line.decode('utf-8') for line in response.readlines()]
            
        reader = csv.DictReader(lines)
        subscribers = []
        for raw_row in reader:
            row = {}
            for k, v in raw_row.items():
                if not k: continue
                k_lower = k.lower()
                val = v.strip() if v else ""
                
                if "email" in k_lower:
                    row["Email"] = val
                elif "name" in k_lower:
                    row["Name"] = val
                elif "expertise" in k_lower or "best describes" in k_lower:
                    row["Expertise Level"] = val
                elif "time" in k_lower or "dedicate" in k_lower:
                    row["Reading Time"] = val
                elif "frequency" in k_lower or "often" in k_lower:
                    row["Report Frequency"] = val
                elif "fields" in k_lower or ("interest" in k_lower and "outside" not in k_lower):
                    row["Interests"] = val
                elif "types" in k_lower or "preferences" in k_lower:
                    row["Discovery Preferences"] = val
                elif "outside" in k_lower or "exploration" in k_lower:
                    row["Exploration Preference"] = val
                elif "consent" in k_lower:
                    row["Consent"] = val

            # Default missing consent column to yes so it doesn't fail if they forgot the question
            if "Consent" not in row:
                row["Consent"] = "yes"

            # Only include users who consented and provided an email
            if row.get("Email") and str(row.get("Consent", "yes")).strip().lower() == "yes":
                subscribers.append(row)
                
        print(f"✅ Loaded {len(subscribers)} active subscribers.")
        return subscribers
        
    except urllib.error.URLError as e:
        print(f"❌ Error fetching Google Sheet. Is it Published to the Web? {e}")
        print("⚠️ No subscribers loaded. Please configure GOOGLE_SHEET_ID or NOETICA_SUBSCRIBERS.")
        return []
    except Exception as e:
        print(f"❌ Unexpected error reading subscribers: {e}")
        return []

def get_paper_limit_for_time(reading_time: str) -> int:
    """Map reading time to number of papers."""
    mapping = {
        "5 Minutes": 3,
        "10 Minutes": 5,
        "15 Minutes": 10,
        "30 Minutes": 20,
        "60 Minutes": 40,
        "120 Minutes": 80
    }
    return mapping.get(reading_time, 10)

def parse_interests(interest_str: str) -> list[str]:
    """Parse comma-separated interests into a list."""
    if not interest_str or interest_str.lower() == "all":
        return []
    return [i.strip() for i in interest_str.split(",")]

def parse_discovery_preferences(pref_str: str) -> list[str]:
    """Map Google Form checkbox strings to system source types."""
    if not pref_str:
        # Default to papers if nothing selected
        return ["paper"]
        
    pref_str = pref_str.lower()
    types = set()
    
    if "research papers" in pref_str or "scientific conferences" in pref_str:
        types.add("paper")
    if "patents" in pref_str:
        types.add("patent")
    if "research grants" in pref_str:
        types.add("grant")
    if "startup funding" in pref_str:
        types.add("funding")
    if "open source projects" in pref_str or "datasets" in pref_str:
        types.add("repo")
    if "clinical trials" in pref_str:
        types.add("trial")
        
    # Meta-categories that imply wanting papers/general intelligence
    if "cross-disciplinary" in pref_str or "emerging frontiers" in pref_str or "forecasts" in pref_str:
        types.add("paper")
        
    return list(types) if types else ["paper"]

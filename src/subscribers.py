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
        print("⚠️  No GOOGLE_SHEET_ID found. Defaulting to single-user mode (RECIPIENT_EMAIL).")
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
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    print(f"📥 Fetching subscribers from Google Sheet...")
    
    try:
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            lines = [line.decode('utf-8') for line in response.readlines()]
            
        reader = csv.DictReader(lines)
        subscribers = []
        for row in reader:
            # Only include users who consented and provided an email
            if row.get("Email") and str(row.get("Consent", "")).strip().lower() == "yes":
                subscribers.append(row)
                
        print(f"✅ Loaded {len(subscribers)} active subscribers.")
        return subscribers
        
    except urllib.error.URLError as e:
        print(f"❌ Error fetching Google Sheet. Is it Published to the Web? {e}")
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

"""
Scientific Intelligence Engine — Feedback Loop
Generates pre-filled Google Form URLs for per-discovery feedback buttons.
When clicked, the link opens a Google Form pre-filled with:
  - discovery_id
  - subscriber_email
  - rating (Very Useful / Useful / Neutral / Not Useful)

The form response lands in a Google Sheet, which GitHub Actions reads
the next morning to boost/penalize discovery scores via database.save_feedback().

SETUP (one-time, manual):
  1. Create a Google Form with fields:
       - Discovery ID   (Short Text)
       - Email          (Short Text)
       - Rating         (Multiple Choice: Very Useful, Useful, Neutral, Not Useful)
  2. Get the pre-fill URL:
       Open the form → ⋮ → Get pre-filled link → fill dummy values → Get link
       The URL will look like:
       https://docs.google.com/forms/d/e/FORM_ID/viewform?usp=pp_url
         &entry.XXXXXXX=DISCOVERY_ID
         &entry.YYYYYYY=EMAIL
         &entry.ZZZZZZZ=RATING
  3. Set the env var FEEDBACK_FORM_BASE_URL to that template URL
     (with the dummy values replaced by {discovery_id}, {email}, {rating})
  4. Add FEEDBACK_SHEET_ID to GitHub Secrets so the feedback sheet can be read.
"""

import os
import csv
import urllib.request
import urllib.parse


FEEDBACK_FORM_BASE = os.environ.get("FEEDBACK_FORM_BASE_URL", "")
FEEDBACK_SHEET_ID  = os.environ.get("FEEDBACK_SHEET_ID", "")

# Rating labels and their URL-safe values
RATINGS = ["Very Useful", "Useful", "Neutral", "Not Useful"]

RATING_COLORS = {
    "Very Useful": "#059669",  # green
    "Useful":      "#2563eb",  # blue
    "Neutral":     "#64748b",  # gray
    "Not Useful":  "#dc2626",  # red
}


def build_feedback_url(discovery_id: str, email: str, rating: str) -> str:
    """
    Build a pre-filled Google Form URL for one rating option.
    Falls back to a simple mailto if FEEDBACK_FORM_BASE_URL is not set.
    """
    if not FEEDBACK_FORM_BASE:
        # Graceful fallback: mailto-based (no form setup needed)
        subject = urllib.parse.quote(f"Feedback:{rating}:{discovery_id}")
        return f"mailto:{email}?subject={subject}"

    url = FEEDBACK_FORM_BASE
    url = url.replace("{discovery_id}", urllib.parse.quote(discovery_id))
    url = url.replace("{email}",        urllib.parse.quote(email))
    url = url.replace("{rating}",       urllib.parse.quote(rating))
    return url


def build_feedback_buttons_html(discovery_id: str, email: str) -> str:
    """
    Generate HTML feedback buttons for a single discovery card.
    Each button is a pre-filled Google Form link.
    """
    buttons = []
    for rating in RATINGS:
        url   = build_feedback_url(discovery_id, email, rating)
        color = RATING_COLORS[rating]
        buttons.append(
            f'<a href="{url}" style="'
            f'background:#f8fafc;border:1px solid {color};color:{color};'
            f'padding:5px 12px;border-radius:6px;text-decoration:none;'
            f'font-size:11px;font-weight:600;margin:0 3px;display:inline-block;">'
            f'{rating}</a>'
        )
    return (
        '<div style="margin-top:12px;padding-top:12px;border-top:1px solid #f1f5f9;">'
        '<span style="color:#94a3b8;font-size:11px;margin-right:8px;">Was this useful?</span>'
        + "".join(buttons)
        + "</div>"
    )


def build_global_feedback_footer_html(email: str) -> str:
    """Footer feedback buttons for the overall digest (not per-discovery)."""
    ratings = ["Very Useful", "Useful", "Neutral", "Not Useful"]
    buttons = []
    for rating in ratings:
        url   = build_feedback_url("digest", email, rating)
        color = RATING_COLORS[rating]
        buttons.append(
            f'<a href="{url}" style="'
            f'background:#f1f5f9;color:{color};border:1px solid {color};'
            f'padding:8px 14px;border-radius:6px;text-decoration:none;'
            f'margin:0 4px;font-size:12px;font-weight:600;">'
            f'{rating}</a>'
        )
    return (
        '<p style="margin:0 0 20px 0;font-weight:500;">'
        'Was this digest useful?<br><br>'
        + "".join(buttons)
        + "</p>"
    )


def ingest_feedback_from_sheet() -> int:
    """
    Read the feedback Google Sheet and persist new feedback into the DB.
    Expected columns: Timestamp, Discovery ID, Email, Rating
    Returns the number of new feedback rows ingested.
    """
    if not FEEDBACK_SHEET_ID:
        return 0

    from database import save_feedback  # avoid circular at module level

    csv_url = f"https://docs.google.com/spreadsheets/d/{FEEDBACK_SHEET_ID}/export?format=csv"
    try:
        req  = urllib.request.Request(csv_url, headers={"User-Agent": "Noetica/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            lines = [line.decode("utf-8") for line in resp.readlines()]
        reader = csv.DictReader(lines)
        count  = 0
        for row in reader:
            did    = (row.get("Discovery ID") or "").strip()
            email  = (row.get("Email") or "").strip()
            rating = (row.get("Rating") or "").strip()
            if did and rating:
                save_feedback(did, email, rating)
                count += 1
        print(f"📊 Ingested {count} feedback entries from sheet.")
        return count
    except Exception as e:
        print(f"⚠️  Could not read feedback sheet: {e}")
        return 0

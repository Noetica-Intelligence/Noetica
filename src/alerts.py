"""
Scientific Intelligence Engine — Alert System (C13)
Sends immediate out-of-schedule alerts when high-priority signals are detected.

Alert conditions (configurable via ALERT_RULES below):
  1. Breakthrough discovery score >= threshold
  2. FGFR4 / Circadian / HCC signal detected
  3. Nobel-candidate score pattern (very high evidence + novelty + cross-domain)
  4. New field emergence detected
  5. User-defined keyword match

Alerts are sent via the same Gmail SMTP channel as digests.
Subscribers can opt-in to alerts via the Google Form "Discovery Preferences" field.

To avoid alert fatigue:
  - Each alert fires at most once per 24 hours per trigger
  - Alerts have a minimum score threshold
  - Alert history is stored in the DB to prevent duplicates
"""

import os
import json
import datetime
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from database import _connect, get_cursor, execute_query

# ─────────────────────────────────────────────────────────────────────────────
# ALERT RULES
# Add new alert types here. They are evaluated against every discovery.
# ─────────────────────────────────────────────────────────────────────────────

ALERT_RULES: list[dict] = [
    {
        "id":          "breakthrough_score",
        "name":        "🚨 Breakthrough Discovery",
        "description": "Score >= 9.2 — potential landmark paper",
        "condition":   lambda d: float(d.get("scores", {}).get("composite", 0)) >= 9.2,
        "min_score":   9.2,
        "emoji":       "🚨",
    },
    {
        "id":          "fgfr4_signal",
        "name":        "🧬 FGFR4 / HCC Signal",
        "description": "FGFR4 or hepatocellular carcinoma discovery detected",
        "condition":   lambda d: any(
            kw in (d.get("title", "") + " " + d.get("abstract", "")).lower()
            for kw in ["fgfr4", "hepatocellular carcinoma", "hcc inhibitor", "fibroblast growth factor receptor 4"]
        ),
        "min_score":   5.0,
        "emoji":       "🧬",
    },
    {
        "id":          "circadian_signal",
        "name":        "⏰ Circadian / ChronoBase Signal",
        "description": "Chronotherapy or circadian biology breakthrough detected",
        "condition":   lambda d: any(
            kw in (d.get("title", "") + " " + d.get("abstract", "")).lower()
            for kw in ["chronotherapy", "circadian rhythm", "clock gene", "bmal1", "per protein", "cry protein",
                       "chrono-oncology", "time-dependent drug", "chronopharmacology"]
        ),
        "min_score":   5.0,
        "emoji":       "⏰",
    },
    {
        "id":          "nobel_candidate",
        "name":        "🏆 Nobel-Candidate Signal",
        "description": "Score >= 9.5 with cross-disciplinary reach >= 3 fields",
        "condition":   lambda d: (
            float(d.get("scores", {}).get("composite", 0)) >= 9.5
            and len(d.get("cross_disciplinary", [])) >= 3
        ),
        "min_score":   9.5,
        "emoji":       "🏆",
    },
    {
        "id":          "alphafold_class",
        "name":        "🤖 AlphaFold-Class Discovery",
        "description": "AI applied to major biological problem at scale",
        "condition":   lambda d: any(
            kw in (d.get("title", "") + " " + d.get("abstract", "")).lower()
            for kw in ["protein structure prediction", "de novo protein", "molecular dynamics AI",
                       "foundation model biology", "protein language model"]
        ) and float(d.get("scores", {}).get("composite", 0)) >= 7.5,
        "min_score":   7.5,
        "emoji":       "🤖",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# ALERT HISTORY (prevents duplicate alerts)
# ─────────────────────────────────────────────────────────────────────────────

def _init_alert_table():
    conn = _connect()
    cursor = get_cursor(conn)
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS alert_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id         TEXT NOT NULL,
            discovery_id    TEXT NOT NULL,
            fired_date      TEXT NOT NULL,
            UNIQUE(rule_id, discovery_id, fired_date)
        )
    """)
    conn.commit()
    conn.close()


def _already_alerted(rule_id: str, discovery_id: str) -> bool:
    """Returns True if this rule already fired for this discovery today."""
    conn = _connect()
    cursor = get_cursor(conn)
    today = datetime.date.today().isoformat()
    execute_query(cursor, 
        "SELECT 1 FROM alert_history WHERE rule_id=? AND discovery_id=? AND fired_date=?",
        (rule_id, discovery_id, today)
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None


def _record_alert(rule_id: str, discovery_id: str):
    conn = _connect()
    cursor = get_cursor(conn)
    today = datetime.date.today().isoformat()
    execute_query(cursor, 
        "INSERT OR IGNORE INTO alert_history (rule_id, discovery_id, fired_date) VALUES (?,?,?)",
        (rule_id, discovery_id, today)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────────────────────────────────────

def _send_alert_email(subject: str, html_body: str, recipients: list[str]):
    """Send an alert email via Gmail SMTP."""
    sender_email    = os.environ.get("SENDER_EMAIL") or os.environ.get("GMAIL_EMAIL", "")
    sender_password = os.environ.get("SENDER_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD", "")

    if not sender_email or not sender_password:
        print("⚠️  Alert: no SMTP credentials found — skipping email send.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = sender_email
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
        print(f"🚨 Alert sent to {len(recipients)} recipient(s): {subject}")
    except Exception as e:
        print(f"❌ Alert email failed: {e}")


def _build_alert_html(rule: dict, discovery: dict) -> str:
    """Build a minimal, focused alert email body."""
    title    = discovery.get("title", "Untitled")
    abstract = (discovery.get("abstract") or "")[:400]
    url      = discovery.get("url", "#")
    domain   = discovery.get("domain", "")
    score    = discovery.get("scores", {}).get("composite", 0)
    today    = datetime.date.today().strftime("%B %d, %Y")

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="font-family:-apple-system,sans-serif;background:#0f172a;margin:0;padding:40px 20px;">
  <div style="max-width:600px;margin:0 auto;background:#1e293b;border-radius:16px;padding:32px;border:1px solid #334155;">
    <div style="font-size:11px;letter-spacing:3px;color:#94a3b8;text-transform:uppercase;margin-bottom:8px;">
      Noetica Intelligence Alert — {today}
    </div>
    <div style="font-size:36px;margin-bottom:16px;">{rule['emoji']}</div>
    <h1 style="color:#f1f5f9;font-size:18px;margin:0 0 8px 0;">{rule['name']}</h1>
    <p style="color:#94a3b8;font-size:13px;margin:0 0 24px 0;">{rule['description']}</p>

    <div style="background:#0f172a;border-radius:12px;padding:20px;margin-bottom:20px;">
      <div style="color:#64748b;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">
        {domain} &nbsp;·&nbsp; Score: {score:.1f}/10
      </div>
      <h2 style="color:#e2e8f0;font-size:16px;margin:0 0 12px 0;">{title}</h2>
      <p style="color:#94a3b8;font-size:13px;line-height:1.7;margin:0 0 16px 0;">{abstract}...</p>
      <a href="{url}" style="background:#2563eb;color:#fff;padding:8px 18px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;">
        Read Now →
      </a>
    </div>

    <p style="color:#475569;font-size:11px;margin:0;text-align:center;">
      Noetica Scientific Intelligence System — Priority Alert
    </p>
  </div>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def check_and_fire_alerts(discoveries: list[dict], subscribers: list[dict]) -> int:
    """
    Evaluate all ALERT_RULES against all discoveries.
    For each match, send an alert email to opted-in subscribers.
    Returns total number of alerts fired.
    """
    _init_alert_table()

    # Only subscribers who selected "Research Papers" or "Emerging Frontiers"
    # in their Discovery Preferences are considered for alerts.
    def _wants_alerts(sub: dict) -> bool:
        prefs = (sub.get("Discovery Preferences") or "").lower()
        return "emerging" in prefs or "breakthrough" in prefs or prefs == ""

    alert_subscribers = [s for s in subscribers if _wants_alerts(s)]
    if not alert_subscribers:
        return 0

    alert_emails = [s.get("Email", "") for s in alert_subscribers if s.get("Email")]
    total_fired  = 0

    for discovery in discoveries:
        did = discovery.get("id", "")
        if not did:
            continue

        for rule in ALERT_RULES:
            try:
                if not rule["condition"](discovery):
                    continue
            except Exception:
                continue

            if _already_alerted(rule["id"], did):
                continue

            score = float(discovery.get("scores", {}).get("composite", 0))
            if score < rule.get("min_score", 0):
                continue

            # Fire alert
            title   = discovery.get("title", "Untitled")[:60]
            subject = f"{rule['emoji']} Noetica Alert: {rule['name']} — {title}..."
            html    = _build_alert_html(rule, discovery)

            _send_alert_email(subject, html, alert_emails)
            _record_alert(rule["id"], did)
            total_fired += 1

    return total_fired


if __name__ == "__main__":
    print(f"Alert System — {len(ALERT_RULES)} rules loaded:")
    for r in ALERT_RULES:
        print(f"  {r['emoji']} {r['name']} (min score: {r['min_score']})")

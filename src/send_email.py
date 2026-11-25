"""
Scientific Intelligence Engine — Email Sender
Sends the daily digest via Gmail SMTP with App Password authentication.
All credentials must be provided via environment variables or GitHub Secrets.
"""

import os
import json
import logging
import textwrap
from build_email import build_email_html
import smtplib
import datetime
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ─────────────────────────────────────────────
# CONFIGURATION (via environment variables)
# ─────────────────────────────────────────────

SENDER_EMAIL    = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")   # Gmail App Password
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "")   # Your inbox
RESEND_API_KEY  = os.environ.get("RESEND_API_KEY", "")    # V3 Delivery
SENDGRID_API_KEY= os.environ.get("SENDGRID_API_KEY", "")  # V3 Delivery

_INITIAL_ENV = {
    "SENDER_EMAIL": SENDER_EMAIL,
    "SENDER_PASSWORD": SENDER_PASSWORD,
    "RECIPIENT_EMAIL": RECIPIENT_EMAIL,
    "RESEND_API_KEY": RESEND_API_KEY,
    "SENDGRID_API_KEY": SENDGRID_API_KEY,
}

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _cfg(name: str) -> str:
    """Resolve config dynamically from os.environ while honoring monkeypatched module globals."""
    mod_val = str(globals().get(name, "") or "")
    env_val = os.environ.get(name)
    if env_val is None:
        return mod_val if mod_val != _INITIAL_ENV.get(name, "") else ""
    if env_val != _INITIAL_ENV.get(name, ""):
        return env_val
    return mod_val or env_val


def validate_config() -> bool:
    """Ensure all required env vars are set."""
    sender_email = _cfg("SENDER_EMAIL")
    sender_password = _cfg("SENDER_PASSWORD")
    recipient_email = _cfg("RECIPIENT_EMAIL")
    resend_key = _cfg("RESEND_API_KEY")
    sendgrid_key = _cfg("SENDGRID_API_KEY")

    missing = []
    if not sender_email:
        missing.append("SENDER_EMAIL")
    
    # We only strictly need SENDER_PASSWORD if no V3 API keys exist
    if not sender_password and not resend_key and not sendgrid_key:
        missing.append("SENDER_PASSWORD (or RESEND_API_KEY/SENDGRID_API_KEY)")
        
    if not recipient_email:
        missing.append("RECIPIENT_EMAIL")
        
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Set them as GitHub Secrets or local environment variables.")
        return False
    return True


def _send_via_resend(
    target_email: str,
    subject: str,
    html_body: str,
    sender_email: str | None = None,
    api_key: str | None = None,
    from_label: str = "Noetica Intelligence",
) -> bool:
    sender = sender_email if sender_email is not None else _cfg("SENDER_EMAIL")
    key = api_key if api_key is not None else _cfg("RESEND_API_KEY")
    if not sender or not key:
        return False
    print("📧 Sending via Resend API (V3)...")
    url = "https://api.resend.com/emails"
    payload = {
        "from": f"{from_label} <{sender}>",
        "to": [target_email],
        "subject": subject,
        "html": html_body
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in (200, 201):
                print(f"✅ Email sent successfully to {target_email} via Resend")
                return True
    except Exception as e:
        print(f"❌ Resend API failed: {e}")
    return False


def _send_via_sendgrid(
    target_email: str,
    subject: str,
    html_body: str,
    sender_email: str | None = None,
    api_key: str | None = None,
    from_label: str = "Noetica Intelligence",
) -> bool:
    sender = sender_email if sender_email is not None else _cfg("SENDER_EMAIL")
    key = api_key if api_key is not None else _cfg("SENDGRID_API_KEY")
    if not sender or not key:
        return False
    print("📧 Sending via SendGrid API (V3)...")
    url = "https://api.sendgrid.com/v3/mail/send"
    payload = {
        "personalizations": [{"to": [{"email": target_email}]}],
        "from": {"email": sender, "name": from_label},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_body}]
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in (200, 201, 202):
                print(f"✅ Email sent successfully to {target_email} via SendGrid")
                return True
    except Exception as e:
        print(f"❌ SendGrid API failed: {e}")
    return False


def send_digest(subject: str, html_body: str, plain_fallback: str = "", recipient_email: str = "") -> bool:
    """
    Send the digest email using the optimal delivery infrastructure (V3 fallback waterfall).
    Returns True on success, False on failure.
    """
    sender_email = _cfg("SENDER_EMAIL")
    sender_password = _cfg("SENDER_PASSWORD")
    resend_key = _cfg("RESEND_API_KEY")
    sendgrid_key = _cfg("SENDGRID_API_KEY")
    target_email = recipient_email if recipient_email else _cfg("RECIPIENT_EMAIL")
    
    if not sender_email or not target_email:
        print("   ⚠️  Email sending skipped locally (missing SENDER_EMAIL or target email).")
        return False

    # 1. Try Resend
    if resend_key:
        success = _send_via_resend(target_email, subject, html_body, sender_email=sender_email, api_key=resend_key)
        if success: return True
        print("⚠️ Resend failed, falling back to next available provider...")

    # 2. Try SendGrid
    if sendgrid_key:
        success = _send_via_sendgrid(target_email, subject, html_body, sender_email=sender_email, api_key=sendgrid_key)
        if success: return True
        print("⚠️ SendGrid failed, falling back to SMTP...")

    # 3. Fallback to Gmail SMTP
    if not sender_password:
        print("   ⚠️  Email sending skipped locally (missing SENDER_PASSWORD).")
        return False

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"]    = f"Noetica Intelligence System <{sender_email}>"
    msg["To"]      = target_email
    msg["X-Priority"] = "1"

    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)

    if not plain_fallback:
        plain_fallback = "Your Scientific Intelligence Digest is ready. Open in an HTML-capable email client."

    msg_alt.attach(MIMEText(plain_fallback, "plain", "utf-8"))
    msg_alt.attach(MIMEText(html_body,      "html",  "utf-8"))



    try:
        print(f"📧 Connecting to {SMTP_HOST}:{SMTP_PORT} via SMTP...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [target_email], msg.as_string())
        print(f"✅ Email sent successfully to {target_email} via SMTP")
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed. Check App Password.")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Recipient refused: {e}")
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error sending email via SMTP: {e}")
        
    return False


def build_plain_text_summary(papers: list[dict]) -> str:
    """Build plain text fallback for email clients without HTML support."""
    today = datetime.date.today().strftime("%A, %B %d, %Y")
    lines = [
        f"Scientific Intelligence Digest — {today}",
        "=" * 60,
        f"Top {len(papers)} breakthroughs across all fields of human knowledge",
        "",
    ]
    for i, p in enumerate(papers, 1):
        score = p.get("scores", {}).get("composite", 0.0)
        lines += [
            f"#{i} [{score:.1f}/10] [{p.get('domain','?')}]",
            f"Title: {p.get('title','')}",
            f"Source: {p.get('source','')} | Date: {p.get('date','')[:10]}",
            f"Authors: {', '.join((a or 'Unknown') for a in (p.get('authors') or [])[:3])}",
            f"URL: {p.get('url','')}",
            f"Abstract: {textwrap.shorten(p.get('abstract',''), width=300, placeholder='...')}",
            "-" * 50,
            "",
        ]
    lines += [
        "Powered by: arXiv · PubMed · OpenAlex · bioRxiv · Semantic Scholar",
        "Ranking: Evidence-first. No social media signals.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # Test mode: send a test email with dummy content
    print("Running in test mode...")
    test_subject = "🔬 TEST: Scientific Intelligence Digest"
    test_html = """
    <html><body style="background:#020817;color:#e2e8f0;font-family:sans-serif;padding:40px;">
    <h1 style="color:#818cf8;">✅ Scientific Intelligence System — Test Email</h1>
    <p style="color:#94a3b8;">If you received this, your Gmail SMTP configuration is working correctly.</p>
    <p style="color:#64748b;font-size:12px;">Sender: SENDER_EMAIL env var | Recipient: RECIPIENT_EMAIL env var</p>
    </body></html>"""
    success = send_digest(test_subject, test_html, "Test email from Scientific Intelligence System.")
    exit(0 if success else 1)

"""
Scientific Intelligence Engine — Email Sender
Sends the daily digest via Gmail SMTP with App Password authentication.
All credentials must be provided via environment variables or GitHub Secrets.
"""

import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ─────────────────────────────────────────────
# CONFIGURATION (via environment variables)
# ─────────────────────────────────────────────

SENDER_EMAIL    = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")   # Gmail App Password
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "")   # Your inbox

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def validate_config() -> bool:
    """Ensure all required env vars are set."""
    missing = []
    if not SENDER_EMAIL:
        missing.append("SENDER_EMAIL")
    if not SENDER_PASSWORD:
        missing.append("SENDER_PASSWORD")
    if not RECIPIENT_EMAIL:
        missing.append("RECIPIENT_EMAIL")
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Set them as GitHub Secrets or local environment variables.")
        return False
    return True


def send_digest(subject: str, html_body: str, plain_fallback: str = "", recipient_email: str = "") -> bool:
    """
    Send the digest email via Gmail SMTP.
    Returns True on success, False on failure.
    """
    target_email = recipient_email if recipient_email else RECIPIENT_EMAIL
    
    if not SENDER_EMAIL or not SENDER_PASSWORD or not target_email:
        print("❌ Missing environment variables or target email.")
        return False

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"]    = f"Noetica Intelligence System <{SENDER_EMAIL}>"
    msg["To"]      = target_email
    msg["X-Priority"] = "1"  # Mark as high priority

    # Create the alternative part for text/html
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)

    # Plain text fallback
    if not plain_fallback:
        plain_fallback = "Your Scientific Intelligence Digest is ready. Open in an HTML-capable email client to view the full digest."

    msg_alt.attach(MIMEText(plain_fallback, "plain", "utf-8"))
    msg_alt.attach(MIMEText(html_body,      "html",  "utf-8"))

    # Embed the logo via CID
    try:
        from email.mime.image import MIMEImage
        import pathlib
        
        logo_path = pathlib.Path("assets/logo.png")
        if logo_path.exists():
            with open(logo_path, "rb") as img_file:
                msg_img = MIMEImage(img_file.read())
                msg_img.add_header("Content-ID", "<logo.png>")
                msg_img.add_header("Content-Disposition", "inline", filename="logo.png")
                msg.attach(msg_img)
        else:
            print(f"⚠️  Logo not found at {logo_path}, email will send without embedded logo.")
    except Exception as e:
        print(f"⚠️  Failed to embed logo: {e}")

    try:
        print(f"📧 Connecting to {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [target_email], msg.as_string())
        print(f"✅ Email sent successfully to {target_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed.")
        print("   → Check SENDER_EMAIL and SENDER_PASSWORD (Gmail App Password, not account password)")
        print("   → Ensure 2FA is enabled on your Gmail account")
        print("   → Generate App Password: myaccount.google.com → Security → App passwords")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Recipient refused: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error sending email: {e}")
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
            f"Authors: {', '.join((p.get('authors') or [])[:3])}",
            f"URL: {p.get('url','')}",
            f"Abstract: {(p.get('abstract',''))[:300]}...",
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

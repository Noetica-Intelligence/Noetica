import smtplib
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path to read from the V2/V3 Database
sys.path.append(str(Path(__file__).parent.parent / "backend"))
from app.database import SessionLocal
from app.models import Discovery

def fetch_top_discoveries(limit=5):
    """Fetch the highest scoring discoveries from the Noetica database."""
    try:
        db = SessionLocal()
        # Get the top items by significance score, prioritizing Breakthroughs
        top_nodes = db.query(Discovery).order_by(Discovery.significance_score.desc()).limit(limit).all()
        return top_nodes
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        db.close()

def generate_html_report(discoveries):
    """Generate a beautiful HTML email report."""
    
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f5; color: #18181b; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #0284c7, #4f46e5); color: white; padding: 30px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 1px; }}
            .header p {{ margin: 10px 0 0 0; font-size: 14px; opacity: 0.9; }}
            .content {{ padding: 30px 20px; }}
            .discovery {{ margin-bottom: 25px; padding-bottom: 25px; border-bottom: 1px solid #e4e4e7; }}
            .discovery:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
            .badge {{ display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }}
            .badge.breakthrough {{ background-color: #fce7f3; color: #db2777; }}
            .badge.emerging {{ background-color: #e0f2fe; color: #0284c7; }}
            .badge.growing {{ background-color: #dcfce7; color: #16a34a; }}
            .title {{ font-size: 18px; font-weight: 700; color: #18181b; margin: 0 0 10px 0; line-height: 1.4; }}
            .domain {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: 600; }}
            .stats {{ font-size: 13px; color: #52525b; background-color: #f8fafc; padding: 10px; border-radius: 6px; margin-top: 15px; border-left: 3px solid #6366f1; }}
            .footer {{ background-color: #18181b; color: #a1a1aa; text-align: center; padding: 20px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NOETICA</h1>
                <p>Scientific Intelligence Daily Report • {date_str}</p>
            </div>
            <div class="content">
                <p style="font-size: 15px; color: #3f3f46; margin-bottom: 30px; line-height: 1.6;">
                    Here are the most significant scientific discoveries and frontier signals detected by the Noetica network today.
                </p>
    """
    
    for d in discoveries:
        # Determine badge class
        badge_class = "emerging"
        if "Breakthrough" in d.status: badge_class = "breakthrough"
        elif "Growing" in d.status: badge_class = "growing"
            
        prob_pct = int(getattr(d, 'forecast_probability', 0.05) * 100)
        score = f"{d.significance_score:.1f}" if d.significance_score else "N/A"
        
        urls = d.source_urls if d.source_urls else []
        url = urls[0] if urls else "#"
        
        html += f"""
                <div class="discovery">
                    <span class="badge {badge_class}">{d.status}</span>
                    <div class="domain">{d.primary_domain}</div>
                    <h2 class="title"><a href="{url}" style="color: inherit; text-decoration: none;">{d.title}</a></h2>
                    <div class="stats">
                        <strong>Significance Score:</strong> {score}/10 &nbsp;|&nbsp; 
                        <strong>Civilizational Forecast:</strong> {prob_pct}% probability
                    </div>
                </div>
        """
        
    html += """
            </div>
            <div class="footer">
                <p>Noetica Network • Mapping Human Knowledge</p>
                <p>You received this because you are subscribed to Noetica Daily Intelligence.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_email(sender_email, sender_password, recipient_emails, html_content):
    """Send the HTML email via Gmail SMTP."""
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Noetica Scientific Intelligence: {datetime.now().strftime('%b %d')}"
    msg['From'] = f"Noetica <{sender_email}>"
    msg['To'] = ", ".join(recipient_emails)

    # Attach the HTML body
    part = MIMEText(html_content, 'html')
    msg.attach(part)

    print(f"Connecting to Gmail SMTP server...")
    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        
        print(f"Sending intelligence report to {len(recipient_emails)} subscribers...")
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        server.quit()
        print("✅ Daily report sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def main():
    # Credentials from Environment Variables (Injected by GitHub Actions)
    sender_email = os.environ.get("NOETICA_EMAIL")
    sender_password = os.environ.get("NOETICA_APP_PASSWORD") 
    
    # Subscriber list (Can be pulled from Google Sheets via API later)
    subscribers_env = os.environ.get("NOETICA_SUBSCRIBERS")
    
    # Check if we're doing a dry run / test mode locally
    if not sender_email or not sender_password:
        print("⚠️ Missing NOETICA_EMAIL or NOETICA_APP_PASSWORD.")
        print("Running in DRY-RUN mode. HTML report will be generated and saved locally as 'latest_report.html'.")
        
        discoveries = fetch_top_discoveries(10)
        if not discoveries:
            print("No discoveries found in the database. Run ingest_v3.py first.")
            return
            
        html = generate_html_report(discoveries)
        
        # Save locally for review
        with open("latest_report.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Report saved to latest_report.html")
        return
        
    # Production Mode
    recipient_emails = subscribers_env.split(",") if subscribers_env else [sender_email]
    
    discoveries = fetch_top_discoveries(10)
    if not discoveries:
        print("No discoveries to send.")
        return
        
    html_content = generate_html_report(discoveries)
    send_email(sender_email, sender_password, recipient_emails, html_content)

if __name__ == "__main__":
    main()

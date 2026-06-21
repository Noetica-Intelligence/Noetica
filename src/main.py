"""
Scientific Intelligence Engine — Main Orchestrator
Run this daily to fetch, score, filter, and email personalized digests.

Usage:
  python src/main.py                    # Full run (fetch + score + email all)
  python src/main.py --dry-run          # Fetch + score, save HTML but don't send
  python src/main.py --send-test        # Send a quick test email only

GitHub Actions runs this at 08:00 UTC daily.
"""

import os
import sys
import json
import datetime
import argparse
from pathlib import Path

# ─── Local imports ─────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from fetch_papers  import fetch_all_papers
from score_papers  import score_and_rank
from build_email   import build_email_html, build_email_subject
from send_email    import send_digest, build_plain_text_summary
from subscribers   import get_subscribers, get_paper_limit_for_time, parse_interests
from database      import save_discoveries

def parse_args():
    parser = argparse.ArgumentParser(description="Scientific Intelligence Engine")
    parser.add_argument("--dry-run",   action="store_true", help="Don't send email, just save HTML")
    parser.add_argument("--send-test", action="store_true", help="Send a test email only")
    parser.add_argument("--load-cache",action="store_true", help="Load today's cached papers instead of re-fetching")
    return parser.parse_args()

def get_cache_path() -> Path:
    today = datetime.date.today().isoformat()
    return Path("data") / f"papers_{today}.json"

def save_cache(papers: list[dict]) -> None:
    cache_path = get_cache_path()
    cache_path.parent.mkdir(exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"💾 Cached {len(papers)} papers → {cache_path}")

def load_cache() -> list[dict] | None:
    cache_path = get_cache_path()
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            papers = json.load(f)
        print(f"📂 Loaded {len(papers)} papers from cache: {cache_path}")
        return papers
    return None

def save_html_preview(html: str, email_addr: str) -> Path:
    """Save the email HTML locally for inspection."""
    today = datetime.date.today().isoformat()
    safe_email = email_addr.replace("@", "_at_").replace(".", "_")
    out_dir = Path("data") / "digests"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"digest_{today}_{safe_email}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"🖥️  HTML preview saved → {out_path}")
    return out_path

def filter_papers_for_subscriber(all_papers: list[dict], sub: dict) -> list[dict]:
    """Filter global ranked discoveries based on user interests."""
    interests_str = sub.get("Interests", "")
    interests = parse_interests(interests_str)
    exploration = str(sub.get("Exploration Preference", "yes")).strip().lower() == "yes"
    
    # Simple keyword/domain matching
    filtered = []
    for p in all_papers:
        if not interests:
            filtered.append(p)
            continue
            
        domain = p.get("domain", "").lower()
        title = p.get("title", "").lower()
        
        # Check if discovery matches any interest
        matched = any(i.lower() in domain or i.lower() in title for i in interests)
        
        if matched:
            filtered.append(p)
            
    # Add forced exploration
    if exploration and len(filtered) < len(all_papers):
        non_matching = [p for p in all_papers if p not in filtered]
        # Mix in a few top non-matching
        exploration_count = max(1, int(len(filtered) * 0.25))
        filtered.extend(non_matching[:exploration_count])
        
    return filtered

def main() -> int:
    args = parse_args()
    today = datetime.date.today().isoformat()

    print("=" * 60)
    print("🔬 Scientific Intelligence Engine (Final V1 Architecture)")
    print(f"   Date: {today}  |  UTC: {datetime.datetime.utcnow().strftime('%H:%M')}")
    print("=" * 60)

    # ── Test mode ──────────────────────────────────────
    if args.send_test:
        print("\n📧 Sending test email...")
        ok = send_digest(
            "🔬 TEST — Scientific Intelligence System V1",
            "<html><body><h1>System is working!</h1></body></html>",
            "System is working!"
        )
        return 0 if ok else 1

    # ── Fetch subscribers ──────────────────────────────
    subscribers = get_subscribers()
    if not subscribers:
        print("❌ No active subscribers found. Aborting.")
        return 1

    # ── Fetch global papers ────────────────────────────
    if args.load_cache:
        papers = load_cache()
        if papers is None:
            papers = fetch_all_papers()
            save_cache(papers)
    else:
        papers = fetch_all_papers()
        save_cache(papers)

    if not papers:
        print("❌ No papers fetched. Aborting.")
        return 1

    # ── Score global discoveries ───────────────────────
    print(f"\n⚖️  Scoring and ranking all {len(papers)} discoveries globally...")
    scored_papers = score_and_rank(papers, top_n=len(papers))

    # ── Save to Discovery Database ─────────────────────
    print(f"💾 Saving {len(scored_papers)} discoveries to SQLite Knowledge Base...")
    save_discoveries(scored_papers)

    # ── Process each subscriber ────────────────────────
    success_count = 0
    for i, sub in enumerate(subscribers, 1):
        email = sub.get("Email")
        name = sub.get("Name") or email.split("@")[0]
        time_str = sub.get("Reading Time", "15 Minutes")
        limit = get_paper_limit_for_time(time_str)
        
        print(f"\n👤 [{i}/{len(subscribers)}] Processing for: {name} ({email})")
        print(f"   Time limit: {time_str} -> {limit} papers")
        
        # Filter and rank specifically for this user
        user_papers = filter_papers_for_subscriber(scored_papers, sub)
        # Take top N
        user_top_papers = user_papers[:limit]
        
        if not user_top_papers:
            print(f"   ⚠️ No matching papers found for this user's interests.")
            continue
            
        print(f"   🏆 Selected {len(user_top_papers)} personalized papers.")
        
        # Build HTML
        html_body = build_email_html(user_top_papers, today)
        subject   = build_email_subject(user_top_papers, today)
        plain     = build_plain_text_summary(user_top_papers)
        
        preview_path = save_html_preview(html_body, email)
        
        # Override RECIPIENT_EMAIL environment variable for send_email function
        os.environ["RECIPIENT_EMAIL"] = email
        
        if args.dry_run:
            print(f"   🌵 DRY RUN — Email NOT sent to {email}.")
            success_count += 1
        else:
            print(f"   📧 Sending digest email to {email}...")
            if send_digest(subject, html_body, plain):
                success_count += 1

    print("\n" + "=" * 60)
    print(f"✅ Run complete. Sent {success_count}/{len(subscribers)} personalized digests.")
    print("=" * 60)

    return 0 if (args.dry_run or success_count > 0) else 1

if __name__ == "__main__":
    sys.exit(main())

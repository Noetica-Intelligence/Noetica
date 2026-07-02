"""
Scientific Intelligence Engine — Main Orchestrator
Run this daily to fetch, score, filter, and email personalized digests.

Usage:
  python src/main.py                    # Full run (fetch + score + email all)
  python src/main.py --dry-run          # Fetch + score, save HTML but don't send
  python src/main.py --send-test        # Send a quick test email only
  python src/main.py --load-cache       # Use today's cached papers (faster)

GitHub Actions runs this at 02:30 UTC (08:00 AM IST) daily.
"""

import os
import sys
import json
import datetime
import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─── Local imports ──────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from source_registry  import fetch_all_intelligence         # ← NEW: plug-in registry
from score_papers     import score_and_rank
from ai_synthesis     import generate_personalized_synthesis, format_abstract_pointwise
from build_email      import build_email_html, build_email_subject
from send_email       import send_digest, build_plain_text_summary
from subscribers      import get_subscribers, get_paper_limit_for_time, parse_interests, parse_discovery_preferences
from database         import save_discoveries
from alerts           import check_and_fire_alerts           # ← NEW: alert system
from emerging_fields  import get_emerging_trends             # ← NEW: real trend detection
from feedback         import ingest_feedback_from_sheet      # ← NEW: feedback loop


def parse_args():
    parser = argparse.ArgumentParser(description="Noetica Scientific Intelligence Engine")
    parser.add_argument("--dry-run",    action="store_true", help="Don't send email, just save HTML")
    parser.add_argument("--send-test",  action="store_true", help="Send a test email only")
    parser.add_argument("--load-cache", action="store_true", help="Load today's cached papers instead of re-fetching")
    return parser.parse_args()


def get_cache_path() -> Path:
    today = datetime.date.today().isoformat()
    return Path("data") / f"papers_{today}.json"


def save_cache(papers: list[dict]) -> None:
    cache_path = get_cache_path()
    cache_path.parent.mkdir(exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"💾 Cached {len(papers)} discoveries → {cache_path}")


def load_cache() -> list[dict] | None:
    cache_path = get_cache_path()
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            papers = json.load(f)
        print(f"📂 Loaded {len(papers)} discoveries from cache: {cache_path}")
        return papers
    return None


def save_html_preview(html: str, email_addr: str) -> Path:
    """Save the email HTML locally for inspection and as archive."""
    today = datetime.date.today().isoformat()
    safe_email = email_addr.replace("@", "_at_").replace(".", "_")
    out_dir = Path("data") / "digests" / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"digest_{today}_{safe_email}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"🖥️  HTML preview saved → {out_path}")
    return out_path


def filter_papers_for_subscriber(all_papers: list[dict], sub: dict) -> list[dict]:
    """
    Filter global ranked discoveries based on subscriber's stated interests.
    80% interests + 20% forced exploration.
    """
    interests_str = sub.get("Interests", "")
    interests = parse_interests(interests_str)
    
    discovery_prefs_str = sub.get("Discovery Preferences", "")
    allowed_types = parse_discovery_preferences(discovery_prefs_str)
    
    exploration = str(sub.get("Exploration Preference", "yes")).strip().lower() == "yes"

    filtered = []
    for p in all_papers:
        # 1. Enforce Discovery Preferences strictly
        p_types = p.get("source_types", ["paper"])
        if not any(t in allowed_types for t in p_types):
            continue

        # 2. Check if it matches interests
        if not interests:
            filtered.append(p)
            continue

        domain   = (p.get("domain") or "").lower()
        title    = (p.get("title") or "").lower()
        abstract = (p.get("abstract") or "").lower()
        
        # Match if the interest keyword is in the domain, title, or the abstract!
        matched = any(i.lower() in domain or i.lower() in title or i.lower() in abstract for i in interests)

        if matched:
            filtered.append(p)

    # 20% forced exploration — inject top non-matching discoveries (must still match allowed_types!)
    if exploration and len(filtered) < len(all_papers):
        non_matching = [
            p for p in all_papers 
            if p not in filtered and any(t in allowed_types for t in p.get("source_types", ["paper"]))
        ]
        exploration_count = max(1, int(len(filtered) * 0.25))
        filtered.extend(non_matching[:exploration_count])

    return filtered


def main() -> int:
    args  = parse_args()
    today = datetime.date.today().isoformat()

    print("=" * 60)
    print("🔬 Noetica Scientific Intelligence Engine")
    print(f"   Date: {today}  |  UTC: {datetime.datetime.now(datetime.UTC).strftime('%H:%M')}")
    print("=" * 60)

    # ── Test mode ─────────────────────────────────────────────────────────────
    if args.send_test:
        print("\n📧 Sending test email...")
        ok = send_digest(
            "🔬 TEST — Noetica Scientific Intelligence System",
            "<html><body><h1>System is working!</h1></body></html>",
            "System is working!"
        )
        return 0 if ok else 1

    # ── Step 0: Ingest pending feedback from Google Sheet ─────────────────────
    print("\n📊 [0/6] Ingesting subscriber feedback...")
    ingest_feedback_from_sheet()

    # ── Step 1: Fetch subscribers ─────────────────────────────────────────────
    print("\n👥 [1/6] Loading subscribers...")
    subscribers = get_subscribers()
    if not subscribers:
        print("❌ No active subscribers found. Aborting.")
        return 1
    print(f"   ✅ {len(subscribers)} active subscriber(s) loaded.")

    # ── Step 2: Fetch all intelligence from source registry ───────────────────
    print("\n📡 [2/6] Fetching intelligence from all sources...")
    if args.load_cache:
        papers = load_cache()
        if papers is None:
            papers = fetch_all_intelligence()
            save_cache(papers)
    else:
        papers = fetch_all_intelligence()
        save_cache(papers)

    if not papers:
        print("❌ No discoveries fetched. Aborting.")
        return 1

    # ── Step 3: Score and rank globally ───────────────────────────────────────
    print(f"\n⚖️  [3/6] Scoring and ranking {len(papers)} discoveries...")
    scored_papers = score_and_rank(papers, top_n=len(papers))

    # ── Step 3b: Zig Engine Graph & BioSignal Analysis ───────────────────────
    print(f"\n⚡ [3b/6] Running Zig Engine graph analysis...")
    import subprocess
    from pathlib import Path
    
    try:
        project_root = Path(__file__).parent.parent
        zig_dir = project_root / "zig_engine"
        zig_input_path = zig_dir / "input.json"
        
        with open(zig_input_path, "w", encoding="utf-8") as f:
            json.dump(scored_papers, f)
            
        zig_bin_name = "zig_engine.exe" if os.name == "nt" else "zig_engine"
        zig_bin_path = zig_dir / "zig-out" / "bin" / zig_bin_name
            
        if zig_bin_path.exists():
            res = subprocess.run([str(zig_bin_path)], capture_output=True, text=True, cwd=str(zig_dir))
            if res.returncode == 0:
                zig_data = json.loads(res.stdout)
                zig_nodes = {n["id"]: n for n in zig_data.get("nodes", [])}
                
                # Merge zig scores into papers
                for p in scored_papers:
                    p_id = p.get("id")
                    if p_id in zig_nodes:
                        zn = zig_nodes[p_id]
                        # Zig computes a robust network influence score [0, 10]
                        p["network_influence"] = zn.get("influence", 0)
                        p["network_centrality"] = zn.get("centrality", "Isolated")
                        p["biosignal"] = zn.get("primary_signal", "none")
                        
                        # Add a bonus to the final score based on network influence
                        p["composite_score"] = min(10.0, p.get("composite_score", 0) + (zn.get("influence", 0) * 0.2))
                
                # Sort again by updated score
                scored_papers = sorted(scored_papers, key=lambda x: x.get("composite_score", 0), reverse=True)
                print("   ✅ Zig Engine enrichment complete.")
            else:
                print(f"   ⚠️  Zig Engine failed (code {res.returncode}): {res.stderr}")
        else:
            print("   ⚠️  Zig Engine binary not found. Skipping network analysis.")
    except json.JSONDecodeError:
        print("   ⚠️  Zig Engine returned invalid JSON. Skipping network analysis.")
    except Exception as e:
        print(f"   ⚠️  Failed to run Zig Engine: {e}")

    # ── Step 4: Save to Knowledge Base (with trend score + lifecycle) ─────────
    print(f"\n💾 [4/6] Saving to Knowledge Base...")
    save_discoveries(scored_papers)

    # ── Step 4b: Check and fire alerts ────────────────────────────────────────
    alerts_fired = check_and_fire_alerts(scored_papers, subscribers)
    if alerts_fired:
        print(f"   🚨 {alerts_fired} priority alert(s) sent.")

    # ── Step 5: Detect real emerging trends ───────────────────────────────────
    print(f"\n📈 [5/6] Detecting emerging fields...")
    emerging_trends = get_emerging_trends(scored_papers)
    print(f"   ✅ {len(emerging_trends)} emerging trend(s) detected.")

    # ── Step 6: Build and send personalized digests ───────────────────────────
    print(f"\n📧 [6/6] Generating personalized digests...")
    success_count = 0
    for i, sub in enumerate(subscribers, 1):
        email    = sub.get("Email")
        name     = sub.get("Name") or email.split("@")[0]
        time_str = sub.get("Reading Time", "15 Minutes")
        limit    = get_paper_limit_for_time(time_str)
        freq_str = sub.get("Report Frequency", "Daily").lower()

        print(f"\n   👤 [{i}/{len(subscribers)}] {name} ({email}) — {time_str} → {limit} discoveries")

        # Enforce Report Frequency
        if "weekly" in freq_str:
            if datetime.date.today().weekday() != 6: # 6 is Sunday
                print(f"   ⏭️  Skipping (Weekly subscriber; delivers on Sundays)")
                continue
        elif "monthly" in freq_str:
            if datetime.date.today().day != 1:
                print(f"   ⏭️  Skipping (Monthly subscriber; delivers on the 1st)")
                continue

        user_papers = filter_papers_for_subscriber(scored_papers, sub)
        
        # --- Enforce Discovery Type Quota (V2 Feature) ---
        discovery_prefs_str = sub.get("Discovery Preferences", "")
        allowed_types = parse_discovery_preferences(discovery_prefs_str)
        user_top_papers = []
        
        # 1. Guarantee at least 1 of each requested type (if available)
        for t in allowed_types:
            for p in user_papers:
                if t in p.get("source_types", ["paper"]) and p not in user_top_papers:
                    user_top_papers.append(p)
                    break
                    
        # 1b. Guarantee at least 1 for each requested interest/sub-domain
        for interest in parse_interests(sub.get("Interests", "")):
            for p in user_papers:
                d = (p.get("domain") or "").lower()
                t_str = (p.get("title") or "").lower()
                a_str = (p.get("abstract") or "").lower()
                if interest.lower() in d or interest.lower() in t_str or interest.lower() in a_str:
                    if p not in user_top_papers:
                        user_top_papers.append(p)
                        break
                    
        # 2. Fill the rest with the highest scoring remaining discoveries
        for p in user_papers:
            if len(user_top_papers) >= limit:
                break
            if p not in user_top_papers:
                user_top_papers.append(p)
                
        # Sort again by score to ensure they appear in order of importance
        user_top_papers = sorted(user_top_papers, key=lambda x: x.get("composite_score", 0), reverse=True)

        if not user_top_papers:
            print(f"   ⚠️  No matching discoveries for this subscriber's interests.")
            continue

        print(f"   🏆 Selected {len(user_top_papers)} personalized discoveries.")
        
        print(f"   ✍️  Formatting abstracts for clarity...")
        for p in user_top_papers:
            if "structured_abstract" not in p:
                p["structured_abstract"] = format_abstract_pointwise(p.get("abstract", ""))

        # Generate Personalized AI Synthesis
        expertise_str = sub.get("Expertise Level", "Intermediate")
        interests_str = sub.get("Interests", "All")
        print(f"   🧠 Generating AI synthesis for expertise: {expertise_str}...")
        ai_synthesis_html = generate_personalized_synthesis(user_top_papers, expertise_str, interests_str)

        # Build email with real emerging trends and AI synthesis
        html_body = build_email_html(user_top_papers, today, emerging_trends=emerging_trends, subscriber_email=email, ai_synthesis_html=ai_synthesis_html)
        subject   = build_email_subject(user_top_papers, today)
        plain     = build_plain_text_summary(user_top_papers)

        save_html_preview(html_body, email)
        os.environ["RECIPIENT_EMAIL"] = email

        if args.dry_run:
            print(f"   🌵 DRY RUN — Email NOT sent to {email}.")
            success_count += 1
        else:
            print(f"   📧 Sending to {email}...")
            if send_digest(subject, html_body, plain, recipient_email=email):
                success_count += 1

    print("\n" + "=" * 60)
    print(f"✅ Run complete. {success_count}/{len(subscribers)} digests sent. {alerts_fired} alerts fired.")
    print("=" * 60)

    return 0 if (args.dry_run or success_count > 0) else 1


if __name__ == "__main__":
    sys.exit(main())

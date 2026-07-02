"""
Noetica Web Dashboard Generator
Builds a static HTML dashboard from the latest knowledge base for GitHub Pages.
"""

import json
from pathlib import Path
import html as html_lib

def generate_dashboard():
    kb_path = Path("data") / "knowledge_base.json"
    if not kb_path.exists():
        print("Knowledge base not found. Cannot generate dashboard.")
        return

    with open(kb_path, "r", encoding="utf-8") as f:
        papers = json.load(f)

    # Sort by score
    papers = sorted(papers, key=lambda x: x.get("composite_score", 0), reverse=True)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Noetica Intelligence Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .header h1 {{ color: #38bdf8; font-weight: 800; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }}
            .card h3 {{ margin-top: 0; font-size: 16px; color: #e2e8f0; }}
            .domain {{ background: #0ea5e9; color: #fff; font-size: 11px; padding: 4px 8px; border-radius: 4px; font-weight: 600; display: inline-block; margin-bottom: 10px; }}
            .score {{ float: right; font-weight: 800; color: #10b981; }}
            .authors {{ color: #94a3b8; font-size: 12px; margin-bottom: 10px; }}
            .abstract {{ font-size: 14px; color: #cbd5e1; line-height: 1.5; }}
            a {{ color: #38bdf8; text-decoration: none; font-weight: 600; font-size: 13px; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Noetica Intelligence Archive</h1>
            <p>Tracking {len(papers)} high-signal discoveries across the global network.</p>
        </div>
        <div class="grid">
    """

    for p in papers[:100]: # Top 100 for web
        title = html_lib.escape(p.get("title", ""))
        domain = html_lib.escape(p.get("domain", "Unknown"))
        score = p.get("composite_score", 0)
        authors = ", ".join(html_lib.escape(a or "Unknown") for a in (p.get("authors") or [])[:3])
        abs_raw = p.get("abstract", "")
        abstract = html_lib.escape(abs_raw[:250] + "..." if len(abs_raw) > 250 else abs_raw)
        url = p.get("url", "#")

        html += f"""
            <div class="card">
                <div class="domain">{domain}</div>
                <div class="score">NET:{score:.1f}</div>
                <h3>{title}</h3>
                <div class="authors">{authors}</div>
                <div class="abstract">{abstract}</div>
                <br>
                <a href="{url}" target="_blank">View Source →</a>
            </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    out_dir = Path("docs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard generated at {out_path}")

if __name__ == "__main__":
    generate_dashboard()

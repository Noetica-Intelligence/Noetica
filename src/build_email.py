"""
Scientific Intelligence Engine — Email Builder
Generates a premium HTML email digest with scoring cards,
cross-domain connections, and wildcard discovery section.
"""

import datetime
import html as html_lib


# ─────────────────────────────────────────────
# DOMAIN → COLOR MAPPING (for badge colors)
# ─────────────────────────────────────────────

DOMAIN_COLORS = {
    "Theoretical Physics":   ("#a78bfa", "#1e1b4b"),  # violet
    "Experimental Physics":  ("#818cf8", "#1e1b4b"),
    "Astrophysics":          ("#67e8f9", "#0c4a6e"),
    "Pure Mathematics":      ("#34d399", "#064e3b"),
    "Applied Mathematics":   ("#6ee7b7", "#064e3b"),
    "Statistics":            ("#fcd34d", "#78350f"),
    "AI & Machine Learning": ("#f87171", "#7f1d1d"),
    "Bioinformatics":        ("#4ade80", "#14532d"),
    "Quantum Computing":     ("#c084fc", "#3b0764"),
    "Cryptography":          ("#fb923c", "#431407"),
    "Systems CS":            ("#94a3b8", "#0f172a"),
    "Robotics":              ("#38bdf8", "#0c4a6e"),
    "Materials Science":     ("#a3e635", "#1a2e05"),
    "Oncology":              ("#f472b6", "#500724"),
    "Circadian Biology":     ("#fb923c", "#431407"),
    "AI in Medicine":        ("#f87171", "#450a0a"),
    "Neuroscience":          ("#e879f9", "#3b0764"),
    "Immunology":            ("#2dd4bf", "#042f2e"),
    "Systems Biology":       ("#4ade80", "#052e16"),
    "Synthetic Biology":     ("#86efac", "#052e16"),
    "Structural Biology":    ("#67e8f9", "#0c4a6e"),
    "GNNs for Biology":      ("#c084fc", "#2e1065"),
    "Molecular Dynamics":    ("#a78bfa", "#1e1b4b"),
    "Philosophy":            ("#fbbf24", "#451a03"),
    "Economics":             ("#34d399", "#022c22"),
    "Psychology":            ("#f9a8d4", "#500724"),
    "Computer Science":      ("#60a5fa", "#1e3a5f"),
    "Mathematics":           ("#6ee7b7", "#064e3b"),
    "Physics":               ("#818cf8", "#1e1b4b"),
    "Biology":               ("#4ade80", "#14532d"),
    "Medicine":              ("#f472b6", "#500724"),
    "Engineering":           ("#fb923c", "#431407"),
    "default":               ("#94a3b8", "#0f172a"),
}

SCORE_COLOR = {
    "high":   "#10b981",  # emerald
    "medium": "#f59e0b",  # amber
    "low":    "#ef4444",  # red
}


def score_color(score: float) -> str:
    if score >= 7.5:
        return SCORE_COLOR["high"]
    elif score >= 5.0:
        return SCORE_COLOR["medium"]
    return SCORE_COLOR["low"]


def score_bar(score: float) -> str:
    """Generate a mini HTML score bar."""
    pct = int(score * 10)
    col = score_color(score)
    return f"""
    <div style="display:flex;align-items:center;gap:8px;margin-top:4px;">
      <div style="flex:1;background:#1e293b;border-radius:4px;height:6px;overflow:hidden;">
        <div style="width:{pct}%;background:{col};height:100%;border-radius:4px;"></div>
      </div>
      <span style="color:{col};font-size:12px;font-weight:700;min-width:32px;">{score:.1f}</span>
    </div>"""


def domain_badge(domain: str) -> str:
    fg, bg = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["default"])
    esc = html_lib.escape(domain)
    return f'<span style="background:{bg};color:{fg};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;letter-spacing:0.5px;">{esc}</span>'


def cross_domain_tags(domains: list[str]) -> str:
    if not domains:
        return ""
    tags = " ".join(
        f'<span style="background:#1e293b;color:#94a3b8;padding:2px 8px;border-radius:12px;font-size:10px;">'
        f'→ {html_lib.escape(d)}</span>'
        for d in domains[:4]
    )
    return f'<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:4px;">{tags}</div>'


def paper_card(rank: int, discovery: dict) -> str:
    """Generate a full discovery card HTML block."""
    title    = html_lib.escape(discovery.get("title", "Untitled"))
    abstract = html_lib.escape((discovery.get("abstract") or "")[:500])
    authors  = ", ".join(html_lib.escape(a) for a in (discovery.get("authors") or [])[:3])
    if len(discovery.get("authors") or []) > 3:
        authors += " et al."
    date     = discovery.get("date", "")[:10]
    source   = html_lib.escape(discovery.get("source", ""))
    url      = discovery.get("url", "#")
    pdf_url  = discovery.get("pdf_url", "")
    domain   = discovery.get("domain", "Other")
    scores   = discovery.get("scores", {})
    cross    = discovery.get("cross_disciplinary", [])
    explanation = discovery.get("explanation", {})
    status   = discovery.get("status", "Emerging")

    composite  = scores.get("composite", 0.0)
    novelty    = scores.get("novelty", 0.0)
    evidence   = scores.get("evidence", 0.0)
    recency    = scores.get("recency", 0.0)

    rank_emoji = ["🥇","🥈","🥉"] + ["🔬"]*97
    em = rank_emoji[min(rank-1, len(rank_emoji)-1)]

    pdf_btn = ""
    if pdf_url:
        pdf_btn = f' &nbsp;<a href="{pdf_url}" style="background:#334155;color:#94a3b8;padding:4px 12px;border-radius:6px;text-decoration:none;font-size:11px;">📄 PDF</a>'

    # Build Explanation Details
    expl_html = ""
    for k, v in explanation.items():
        expl_html += f'<tr><td style="color:#64748b;font-size:11px;padding-bottom:6px;width:120px;">{k}</td><td style="padding-bottom:6px;color:#cbd5e1;font-size:11px;font-weight:600;">{v}</td></tr>'

    # Status Color
    status_color = "#38bdf8"
    if status == "Breakthrough": status_color = "#f472b6"
    elif status == "Growing": status_color = "#4ade80"

    return f"""
    <div style="background:#0f172a;border:1px solid #1e293b;border-radius:16px;padding:24px;margin-bottom:20px;box-shadow:0 4px 24px rgba(0,0,0,0.4);">

      <!-- Header Row -->
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:24px;">{em}</span>
          <span style="color:#64748b;font-size:13px;font-weight:600;">#{rank}</span>
          {domain_badge(domain)}
          <span style="border:1px solid {status_color};color:{status_color};padding:2px 6px;border-radius:4px;font-size:9px;text-transform:uppercase;letter-spacing:1px;">{status}</span>
        </div>
        <div style="text-align:right;">
          <div style="color:{score_color(composite)};font-size:22px;font-weight:800;">{composite:.1f}<span style="font-size:12px;color:#475569;">/10</span></div>
          <div style="color:#475569;font-size:10px;">IMPACT SCORE</div>
        </div>
      </div>

      <!-- Title -->
      <h2 style="margin:0 0 8px 0;font-size:17px;font-weight:700;line-height:1.4;">
        <a href="{url}" style="color:#e2e8f0;text-decoration:none;">{title}</a>
      </h2>

      <!-- Authors & Date -->
      <div style="color:#64748b;font-size:12px;margin-bottom:12px;">
        {authors} &nbsp;·&nbsp; {date} &nbsp;·&nbsp; <span style="color:#475569;">{source}</span>
      </div>

      <!-- Abstract -->
      <p style="color:#94a3b8;font-size:13px;line-height:1.7;margin:0 0 16px 0;border-left:3px solid #1e293b;padding-left:12px;">
        {abstract}{"..." if len(discovery.get("abstract",""))>500 else ""}
      </p>

      <!-- Ranking Explanation -->
      <div style="background:#060c18;border-radius:10px;padding:14px;margin-bottom:12px;">
        <div style="color:#475569;font-size:10px;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">Ranking Explanation</div>
        <table style="width:100%;border-collapse:collapse;">
          {expl_html}
        </table>
      </div>

      <!-- Cross-disciplinary -->
      {f'<div style="color:#475569;font-size:10px;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">⚡ Cross-Disciplinary Impact</div>' if cross else ""}
      {cross_domain_tags(cross)}

      <!-- Action Buttons -->
      <div style="margin-top:14px;">
        <a href="{url}" style="background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;padding:6px 16px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;">🔗 Read Paper</a>
        {pdf_btn}
      </div>

    </div>"""


def emerging_trend_item(topic: str, desc: str) -> str:
    return f"""
    <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;">
      <span style="color:#f59e0b;font-size:16px;min-width:20px;">◈</span>
      <div>
        <div style="color:#e2e8f0;font-size:13px;font-weight:600;">{html_lib.escape(topic)}</div>
        <div style="color:#64748b;font-size:12px;">{html_lib.escape(desc)}</div>
      </div>
    </div>"""


def build_email_html(papers: list[dict], date_str: str) -> str:
    """Build the complete HTML email from ranked papers."""
    today = datetime.date.today().strftime("%A, %B %d, %Y")
    total = len(papers)

    # Wildcard: pick the last paper (most different domain from top)
    wildcard = papers[-1] if total > 1 else None
    main_papers = papers[:-1] if wildcard else papers

    # Stats
    domains_covered = len(set(p.get("domain","") for p in papers))
    sources_covered = len(set(p.get("source","") for p in papers))
    avg_score = sum(p.get("scores",{}).get("composite",0) for p in papers) / max(total, 1)

    # Build paper cards
    cards_html = "\n".join(paper_card(i+1, p) for i, p in enumerate(main_papers))

    # Wildcard card
    wildcard_html = ""
    if wildcard:
        wc_title  = html_lib.escape(wildcard.get("title",""))
        wc_abs    = html_lib.escape((wildcard.get("abstract",""))[:400])
        wc_url    = wildcard.get("url","#")
        wc_domain = wildcard.get("domain","")
        wildcard_html = f"""
        <div style="background:linear-gradient(135deg,#1a0533,#0f172a);border:1px solid #6d28d9;border-radius:16px;padding:24px;margin-bottom:20px;">
          <div style="color:#a78bfa;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">🎲 WILDCARD DISCOVERY</div>
          <div style="color:#64748b;font-size:11px;margin-bottom:6px;">{domain_badge(wc_domain)}</div>
          <h3 style="color:#e2e8f0;font-size:16px;margin:8px 0;">
            <a href="{wc_url}" style="color:#e2e8f0;text-decoration:none;">{wc_title}</a>
          </h3>
          <p style="color:#94a3b8;font-size:13px;line-height:1.6;margin:8px 0;">{wc_abs}{"..." if len(wildcard.get("abstract",""))>400 else ""}</p>
          <div style="color:#64748b;font-size:11px;margin-top:10px;">Why this matters: Cross-disciplinary insights often come from unexpected fields.</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scientific Intelligence Digest — {today}</title>
</head>
<body style="margin:0;padding:0;background:#020817;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;color:#e2e8f0;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#020817;">
    <tr><td align="center" style="padding:30px 20px;">

      <!-- Container -->
      <table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%;">
        <tr><td>

          <!-- ══ HEADER ══ -->
          <div style="background:linear-gradient(135deg,#0d0221 0%,#1a0533 40%,#0c1a3d 100%);border-radius:20px;padding:40px 36px;margin-bottom:20px;text-align:center;border:1px solid #1e1b4b;">
            <div style="font-size:12px;letter-spacing:3px;color:#6d28d9;text-transform:uppercase;margin-bottom:8px;">Scientific Intelligence System</div>
            <h1 style="margin:0 0 8px 0;font-size:32px;font-weight:800;background:linear-gradient(90deg,#818cf8,#c084fc,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
              Daily Research Digest
            </h1>
            <p style="margin:0;color:#64748b;font-size:14px;">{today}</p>
            <div style="margin-top:20px;display:flex;justify-content:center;gap:24px;">
              <div style="text-align:center;">
                <div style="color:#a78bfa;font-size:24px;font-weight:800;">{total}</div>
                <div style="color:#475569;font-size:10px;letter-spacing:1px;">PAPERS</div>
              </div>
              <div style="color:#1e293b;font-size:30px;">|</div>
              <div style="text-align:center;">
                <div style="color:#34d399;font-size:24px;font-weight:800;">{domains_covered}</div>
                <div style="color:#475569;font-size:10px;letter-spacing:1px;">DOMAINS</div>
              </div>
              <div style="color:#1e293b;font-size:30px;">|</div>
              <div style="text-align:center;">
                <div style="color:#f472b6;font-size:24px;font-weight:800;">{sources_covered}</div>
                <div style="color:#475569;font-size:10px;letter-spacing:1px;">SOURCES</div>
              </div>
              <div style="color:#1e293b;font-size:30px;">|</div>
              <div style="text-align:center;">
                <div style="color:#fbbf24;font-size:24px;font-weight:800;">{avg_score:.1f}</div>
                <div style="color:#475569;font-size:10px;letter-spacing:1px;">AVG SCORE</div>
              </div>
            </div>
          </div>

          <!-- ══ SECTION LABEL ══ -->
          <div style="color:#475569;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;padding:0 4px;">
            🏆 Top Ranked Discoveries
          </div>

          <!-- ══ PAPER CARDS ══ -->
          {cards_html}

          <!-- ══ WILDCARD ══ -->
          {wildcard_html}

          <!-- ══ EMERGING TRENDS ══ -->
          <div style="background:#0a0f1e;border:1px solid #1e293b;border-radius:16px;padding:24px;margin-bottom:20px;">
            <div style="color:#f59e0b;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">📈 Emerging Trends This Week</div>
            {emerging_trend_item("AI-Assisted Science", "LLMs generating and verifying novel hypotheses")}
            {emerging_trend_item("Quantum-Classical Hybrid Algorithms", "Near-term quantum advantage in optimization")}
            {emerging_trend_item("Circadian Pharmacology", "Timing-dependent drug efficacy across oncology trials")}
            {emerging_trend_item("Foundation Models for Biology", "Protein/DNA/RNA language models converging")}
            {emerging_trend_item("Causal AI", "Moving from correlation to mechanism in ML")}
          </div>

          <!-- ══ FOOTER ══ -->
          <div style="text-align:center;padding:24px;color:#334155;font-size:12px;border-top:1px solid #1e293b;">
            <p style="margin:0 0 16px 0;">
              Was this digest useful?<br>
              <a href="mailto:feedback@scientificintel.local?subject=Very Useful" style="color:#6366f1;text-decoration:none;margin:0 8px;">Very Useful</a> | 
              <a href="mailto:feedback@scientificintel.local?subject=Useful" style="color:#6366f1;text-decoration:none;margin:0 8px;">Useful</a> | 
              <a href="mailto:feedback@scientificintel.local?subject=Neutral" style="color:#6366f1;text-decoration:none;margin:0 8px;">Neutral</a> | 
              <a href="mailto:feedback@scientificintel.local?subject=Not Useful" style="color:#6366f1;text-decoration:none;margin:0 8px;">Not Useful</a>
            </p>
            <p style="margin:0 0 8px 0;">🔬 Scientific Intelligence System &nbsp;·&nbsp; Evidence-First Research Curation</p>
            <p style="margin:0;color:#1e293b;">Powered by arXiv · PubMed · OpenAlex · bioRxiv · Semantic Scholar</p>
            <p style="margin:8px 0 0 0;color:#1e293b;font-size:10px;">Ranking is based on scientific evidence and novelty — not social media popularity.</p>
          </div>

        </td></tr>
      </table>

    </td></tr>
  </table>
</body>
</html>"""


def build_email_subject(papers: list[dict], date_str: str) -> str:
    """Build an attention-grabbing subject line."""
    today = datetime.date.today().strftime("%b %d")
    top = papers[0] if papers else None
    if top:
        short_title = top.get("title","")[:50]
        score = top.get("scores",{}).get("composite",0)
        return f"🔬 [{today}] #{1} [{score:.1f}/10] {short_title}... + {len(papers)-1} more breakthroughs"
    return f"🔬 Scientific Intelligence Digest — {today}"

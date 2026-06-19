"""
Scientific Intelligence Engine — Email Builder
Generates a premium HTML email digest with scoring cards,
cross-domain connections, and wildcard discovery section.
"""

import datetime
import html as html_lib

# ─────────────────────────────────────────────
# DOMAIN → COLOR MAPPING (Light DeepMind Aesthetic)
# ─────────────────────────────────────────────

DOMAIN_COLORS = {
    "Theoretical Physics":   ("#4f46e5", "#e0e7ff"),  # Indigo
    "Experimental Physics":  ("#4338ca", "#e0e7ff"),
    "Astrophysics":          ("#0284c7", "#e0f2fe"),
    "Pure Mathematics":      ("#059669", "#d1fae5"),
    "Applied Mathematics":   ("#059669", "#d1fae5"),
    "Statistics":            ("#d97706", "#fef3c7"),
    "AI & Machine Learning": ("#e11d48", "#ffe4e6"),
    "Bioinformatics":        ("#16a34a", "#dcfce7"),
    "Quantum Computing":     ("#7c3aed", "#ede9fe"),
    "Cryptography":          ("#ea580c", "#ffedd5"),
    "Systems CS":            ("#475569", "#f1f5f9"),
    "Robotics":              ("#0284c7", "#e0f2fe"),
    "Materials Science":     ("#65a30d", "#ecfccb"),
    "Oncology":              ("#db2777", "#fce7f3"),
    "Circadian Biology":     ("#ea580c", "#ffedd5"),
    "AI in Medicine":        ("#e11d48", "#ffe4e6"),
    "Neuroscience":          ("#c026d3", "#fae8ff"),
    "Immunology":            ("#0d9488", "#ccfbf1"),
    "Systems Biology":       ("#16a34a", "#dcfce7"),
    "Synthetic Biology":     ("#16a34a", "#dcfce7"),
    "Structural Biology":    ("#0284c7", "#e0f2fe"),
    "GNNs for Biology":      ("#7c3aed", "#ede9fe"),
    "Molecular Dynamics":    ("#4f46e5", "#e0e7ff"),
    "Philosophy":            ("#b45309", "#fef3c7"),
    "Economics":             ("#059669", "#d1fae5"),
    "Psychology":            ("#db2777", "#fce7f3"),
    "Computer Science":      ("#2563eb", "#dbeafe"),
    "Mathematics":           ("#059669", "#d1fae5"),
    "Physics":               ("#4f46e5", "#e0e7ff"),
    "Biology":               ("#16a34a", "#dcfce7"),
    "Medicine":              ("#db2777", "#fce7f3"),
    "Engineering":           ("#ea580c", "#ffedd5"),
    "default":               ("#475569", "#f1f5f9"),
}

SCORE_COLOR = {
    "high":   "#059669",  # emerald
    "medium": "#d97706",  # amber
    "low":    "#e11d48",  # red
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
      <div style="flex:1;background:#e2e8f0;border-radius:4px;height:6px;overflow:hidden;">
        <div style="width:{pct}%;background:{col};height:100%;border-radius:4px;"></div>
      </div>
      <span style="color:{col};font-size:12px;font-weight:700;min-width:32px;">{score:.1f}</span>
    </div>"""


def domain_badge(domain: str) -> str:
    fg, bg = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["default"])
    esc = html_lib.escape(domain)
    return f'<span style="background:{bg};color:{fg};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600;letter-spacing:0.5px;border:1px solid {fg}33;">{esc}</span>'


def cross_domain_tags(domains: list[str]) -> str:
    if not domains:
        return ""
    tags = " ".join(
        f'<span style="background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;padding:3px 8px;border-radius:6px;font-size:10px;">'
        f'→ {html_lib.escape(d)}</span>'
        for d in domains[:4]
    )
    return f'<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:6px;">{tags}</div>'


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

    rank_emoji = ["1️⃣","2️⃣","3️⃣"] + ["🔬"]*97
    em = rank_emoji[min(rank-1, len(rank_emoji)-1)]

    pdf_btn = ""
    if pdf_url:
        pdf_btn = f' &nbsp;<a href="{pdf_url}" style="background:#f1f5f9;border:1px solid #cbd5e1;color:#475569;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:600;">📄 PDF</a>'

    # Build Explanation Details
    expl_html = ""
    for k, v in explanation.items():
        expl_html += f'<tr><td style="color:#64748b;font-size:12px;padding-bottom:8px;width:130px;">{k}</td><td style="padding-bottom:8px;color:#0f172a;font-size:12px;font-weight:500;">{v}</td></tr>'

    # Status Color
    status_color = "#0284c7"
    if status == "Breakthrough": status_color = "#e11d48"
    elif status == "Growing": status_color = "#16a34a"

    return f"""
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px;margin-bottom:24px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);">

      <!-- Header Row -->
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:12px;">
          <span style="font-size:24px;">{em}</span>
          {domain_badge(domain)}
          <span style="background:#f8fafc;border:1px solid {status_color};color:{status_color};padding:3px 8px;border-radius:6px;font-size:10px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">{status}</span>
        </div>
        <div style="text-align:right;">
          <div style="color:{score_color(composite)};font-size:24px;font-weight:800;line-height:1;">{composite:.1f}<span style="font-size:14px;color:#94a3b8;font-weight:600;">/10</span></div>
          <div style="color:#64748b;font-size:10px;letter-spacing:1px;margin-top:4px;">IMPACT SCORE</div>
        </div>
      </div>

      <!-- Title -->
      <h2 style="margin:0 0 10px 0;font-size:19px;font-weight:700;line-height:1.4;">
        <a href="{url}" style="color:#0f172a;text-decoration:none;">{title}</a>
      </h2>

      <!-- Authors & Date -->
      <div style="color:#64748b;font-size:13px;margin-bottom:16px;font-weight:500;">
        {authors} &nbsp;·&nbsp; {date} &nbsp;·&nbsp; <span style="color:#475569;">{source}</span>
      </div>

      <!-- Abstract -->
      <p style="color:#334155;font-size:14px;line-height:1.7;margin:0 0 20px 0;border-left:3px solid #cbd5e1;padding-left:14px;">
        {abstract}{"..." if len(discovery.get("abstract",""))>500 else ""}
      </p>

      <!-- Ranking Explanation -->
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:16px;">
        <div style="color:#64748b;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;font-weight:600;">AI Ranking Rationale</div>
        <table style="width:100%;border-collapse:collapse;">
          {expl_html}
        </table>
      </div>

      <!-- Cross-disciplinary -->
      {f'<div style="color:#64748b;font-size:10px;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;font-weight:600;">⚡ Cross-Disciplinary Architecture</div>' if cross else ""}
      {cross_domain_tags(cross)}

      <!-- Action Buttons -->
      <div style="margin-top:20px;padding-top:16px;border-top:1px solid #f1f5f9;">
        <a href="{url}" style="background:#2563eb;color:#fff;padding:8px 20px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;display:inline-block;">🔗 Read Publication</a>
        {pdf_btn}
      </div>

    </div>"""


def emerging_trend_item(topic: str, desc: str) -> str:
    return f"""
    <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:12px;">
      <span style="color:#2563eb;font-size:16px;min-width:20px;">◈</span>
      <div>
        <div style="color:#0f172a;font-size:14px;font-weight:700;">{html_lib.escape(topic)}</div>
        <div style="color:#475569;font-size:13px;">{html_lib.escape(desc)}</div>
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
        <div style="background:linear-gradient(to right, #f8fafc, #f1f5f9);border:1px solid #cbd5e1;border-radius:16px;padding:28px;margin-bottom:24px;">
          <div style="color:#7c3aed;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;font-weight:700;">🎲 Wildcard Discovery</div>
          <div style="margin-bottom:8px;">{domain_badge(wc_domain)}</div>
          <h3 style="color:#0f172a;font-size:18px;margin:12px 0;font-weight:700;">
            <a href="{wc_url}" style="color:#0f172a;text-decoration:none;">{wc_title}</a>
          </h3>
          <p style="color:#334155;font-size:14px;line-height:1.6;margin:12px 0;">{wc_abs}{"..." if len(wildcard.get("abstract",""))>400 else ""}</p>
          <div style="color:#64748b;font-size:12px;margin-top:14px;font-style:italic;">Why this matters: Cross-disciplinary insights often emerge from adjacent fields.</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scientific Intelligence Digest — {today}</title>
</head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,Cantarell,sans-serif;color:#0f172a;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;">
    <tr><td align="center" style="padding:40px 20px;">

      <!-- Container -->
      <table width="700" cellpadding="0" cellspacing="0" style="max-width:700px;width:100%;">
        <tr><td>

          <!-- ══ HEADER ══ -->
          <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:20px;padding:40px;margin-bottom:24px;text-align:center;box-shadow:0 10px 25px -5px rgba(0,0,0,0.05);">
            <img src="https://noetica-intelligence.github.io/Noetica/logo.jpg" alt="Noetica Logo" style="width:64px;height:64px;border-radius:50%;margin-bottom:16px;border:2px solid #e2e8f0;">
            <div style="font-size:11px;letter-spacing:3px;color:#64748b;text-transform:uppercase;margin-bottom:12px;font-weight:700;">Noetica Intelligence System</div>
            <h1 style="margin:0 0 12px 0;font-size:32px;font-weight:800;color:#0f172a;letter-spacing:-0.5px;">
              Daily Research Digest
            </h1>
            <p style="margin:0;color:#475569;font-size:15px;font-weight:500;">{today}</p>
            
            <div style="margin-top:32px;padding-top:24px;border-top:1px solid #f1f5f9;display:flex;justify-content:center;gap:32px;">
              <div style="text-align:center;">
                <div style="color:#2563eb;font-size:26px;font-weight:800;">{total}</div>
                <div style="color:#64748b;font-size:10px;letter-spacing:1px;font-weight:600;margin-top:4px;">PAPERS</div>
              </div>
              <div style="color:#e2e8f0;font-size:26px;">|</div>
              <div style="text-align:center;">
                <div style="color:#059669;font-size:26px;font-weight:800;">{domains_covered}</div>
                <div style="color:#64748b;font-size:10px;letter-spacing:1px;font-weight:600;margin-top:4px;">DOMAINS</div>
              </div>
              <div style="color:#e2e8f0;font-size:26px;">|</div>
              <div style="text-align:center;">
                <div style="color:#db2777;font-size:26px;font-weight:800;">{sources_covered}</div>
                <div style="color:#64748b;font-size:10px;letter-spacing:1px;font-weight:600;margin-top:4px;">SOURCES</div>
              </div>
              <div style="color:#e2e8f0;font-size:26px;">|</div>
              <div style="text-align:center;">
                <div style="color:#d97706;font-size:26px;font-weight:800;">{avg_score:.1f}</div>
                <div style="color:#64748b;font-size:10px;letter-spacing:1px;font-weight:600;margin-top:4px;">AVG SCORE</div>
              </div>
            </div>
          </div>

          <!-- ══ SECTION LABEL ══ -->
          <div style="color:#64748b;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:20px;padding:0 8px;font-weight:700;">
            🏆 High-Impact Discoveries
          </div>

          <!-- ══ PAPER CARDS ══ -->
          {cards_html}

          <!-- ══ WILDCARD ══ -->
          {wildcard_html}

          <!-- ══ EMERGING TRENDS ══ -->
          <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px;margin-bottom:24px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="color:#ea580c;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:20px;font-weight:700;">📈 Emerging Trends Assessed</div>
            {emerging_trend_item("AI-Assisted Science", "LLMs generating and verifying novel hypotheses")}
            {emerging_trend_item("Quantum-Classical Hybrid Algorithms", "Near-term quantum advantage in optimization")}
            {emerging_trend_item("Circadian Pharmacology", "Timing-dependent drug efficacy across oncology trials")}
            {emerging_trend_item("Foundation Models for Biology", "Protein/DNA/RNA language models converging")}
            {emerging_trend_item("Causal AI", "Moving from correlation to mechanism in ML")}
          </div>

          <!-- ══ FOOTER ══ -->
          <div style="text-align:center;padding:32px 24px;color:#64748b;font-size:13px;border-top:1px solid #e2e8f0;">
            <p style="margin:0 0 20px 0;font-weight:500;">
              Was this digest useful?<br><br>
              <a href="mailto:feedback@noetica.local?subject=Very Useful" style="background:#f1f5f9;color:#2563eb;padding:8px 12px;border-radius:6px;text-decoration:none;margin:0 4px;">Very Useful</a>
              <a href="mailto:feedback@noetica.local?subject=Useful" style="background:#f1f5f9;color:#2563eb;padding:8px 12px;border-radius:6px;text-decoration:none;margin:0 4px;">Useful</a>
              <a href="mailto:feedback@noetica.local?subject=Neutral" style="background:#f1f5f9;color:#475569;padding:8px 12px;border-radius:6px;text-decoration:none;margin:0 4px;">Neutral</a>
              <a href="mailto:feedback@noetica.local?subject=Not Useful" style="background:#f1f5f9;color:#475569;padding:8px 12px;border-radius:6px;text-decoration:none;margin:0 4px;">Not Useful</a>
            </p>
            <p style="margin:0 0 8px 0;font-weight:600;color:#0f172a;">Noetica Intelligence System</p>
            <p style="margin:0;">Powered by arXiv · PubMed · bioRxiv · Semantic Scholar</p>
            <p style="margin:12px 0 0 0;font-size:11px;color:#94a3b8;">Confidential Intelligence Briefing for Authorized Personnel Only.</p>
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
    return f"🔬 Noetica Intelligence Digest — {today}"

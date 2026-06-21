"""
Scientific Intelligence Engine — Email Builder
Generates a premium dark-mode HTML email digest with scoring cards,
cross-domain connections, and wildcard discovery section.
"""

import datetime
import html as html_lib

# ─────────────────────────────────────────────
# DOMAIN → COLOR MAPPING (Dark Mode Neon Aesthetic)
# ─────────────────────────────────────────────

DOMAIN_COLORS = {
    "Theoretical Physics":   ("#818cf8", "#312e81"),  # Indigo
    "Experimental Physics":  ("#6366f1", "#3730a3"),
    "Astrophysics":          ("#38bdf8", "#075985"),
    "Pure Mathematics":      ("#34d399", "#064e3b"),
    "Applied Mathematics":   ("#34d399", "#064e3b"),
    "Statistics":            ("#fbbf24", "#78350f"),
    "AI & Machine Learning": ("#fb7185", "#881337"),
    "Bioinformatics":        ("#4ade80", "#14532d"),
    "Quantum Computing":     ("#a78bfa", "#4c1d95"),
    "Cryptography":          ("#fdba74", "#7c2d12"),
    "Systems CS":            ("#94a3b8", "#1e293b"),
    "Robotics":              ("#38bdf8", "#075985"),
    "Materials Science":     ("#a3e635", "#3f6212"),
    "Oncology":              ("#f472b6", "#831843"),
    "Circadian Biology":     ("#fb923c", "#7c2d12"),
    "AI in Medicine":        ("#fb7185", "#881337"),
    "Neuroscience":          ("#e879f9", "#701a75"),
    "Immunology":            ("#2dd4bf", "#134e4a"),
    "Systems Biology":       ("#4ade80", "#14532d"),
    "Synthetic Biology":     ("#4ade80", "#14532d"),
    "Structural Biology":    ("#38bdf8", "#075985"),
    "GNNs for Biology":      ("#a78bfa", "#4c1d95"),
    "Molecular Dynamics":    ("#818cf8", "#312e81"),
    "Philosophy":            ("#fcd34d", "#78350f"),
    "Economics":             ("#34d399", "#064e3b"),
    "Psychology":            ("#f472b6", "#831843"),
    "Computer Science":      ("#60a5fa", "#1e3a8a"),
    "Mathematics":           ("#34d399", "#064e3b"),
    "Physics":               ("#818cf8", "#312e81"),
    "Biology":               ("#4ade80", "#14532d"),
    "Medicine":              ("#f472b6", "#831843"),
    "Engineering":           ("#fb923c", "#7c2d12"),
    "default":               ("#cbd5e1", "#1e293b"),
}

SCORE_COLOR = {
    "high":   "#10b981",  # neon emerald
    "medium": "#f59e0b",  # neon amber
    "low":    "#ef4444",  # neon red
}


def score_color(score: float) -> str:
    if score >= 7.5:
        return SCORE_COLOR["high"]
    elif score >= 5.0:
        return SCORE_COLOR["medium"]
    return SCORE_COLOR["low"]


def domain_badge(domain: str) -> str:
    fg, bg = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["default"])
    esc = html_lib.escape(domain)
    return f'<span style="background:{bg};color:{fg};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;letter-spacing:0.5px;border:1px solid {fg}40;">{esc}</span>'


def cross_domain_tags(domains: list[str]) -> str:
    if not domains:
        return ""
    tags = " ".join(
        f'<span style="background:#0f172a;color:#94a3b8;border:1px solid #334155;padding:3px 8px;border-radius:6px;font-size:10px;">'
        f'→ {html_lib.escape(d)}</span>'
        for d in domains[:4]
    )
    return f'<div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:6px;">{tags}</div>'


def paper_card(rank: int, discovery: dict) -> str:
    """Generate a full discovery card HTML block in dark mode."""
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
    col = score_color(composite)

    rank_num = f"#{rank}"
    
    pdf_btn = ""
    if pdf_url:
        pdf_btn = f' &nbsp;<a href="{pdf_url}" style="background:#1e293b;border:1px solid #475569;color:#cbd5e1;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;display:inline-block;transition:all 0.2s;">📄 PDF</a>'

    # Build Explanation Details
    expl_html = ""
    for k, v in explanation.items():
        expl_html += f'<tr><td style="color:#94a3b8;font-size:12px;padding-bottom:8px;width:130px;">{k}</td><td style="padding-bottom:8px;color:#f8fafc;font-size:12px;font-weight:500;">{v}</td></tr>'

    # Status Color
    status_color = "#38bdf8"
    if status == "Breakthrough": status_color = "#f43f5e"
    elif status == "Growing": status_color = "#34d399"

    return f"""
    <div style="background:#0f172a;border:1px solid #1e293b;border-radius:16px;padding:28px;margin-bottom:24px;box-shadow:0 10px 15px -3px rgba(0,0,0,0.5), 0 4px 6px -2px rgba(0,0,0,0.25);">

      <!-- Header Row -->
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:12px;">
          <span style="color:#64748b;font-size:18px;font-weight:800;letter-spacing:-0.5px;">{rank_num}</span>
          {domain_badge(domain)}
          <span style="background:transparent;border:1px solid {status_color};color:{status_color};padding:3px 8px;border-radius:6px;font-size:10px;text-transform:uppercase;letter-spacing:1px;font-weight:700;">{status}</span>
        </div>
        <div style="text-align:right;">
          <div style="color:{col};font-size:24px;font-weight:800;line-height:1;text-shadow: 0 0 10px {col}40;">{composite:.1f}<span style="font-size:14px;color:#475569;font-weight:600;">/10</span></div>
          <div style="color:#64748b;font-size:10px;letter-spacing:1.5px;margin-top:4px;">IMPACT</div>
        </div>
      </div>

      <!-- Title -->
      <h2 style="margin:0 0 10px 0;font-size:20px;font-weight:700;line-height:1.4;">
        <a href="{url}" style="color:#f8fafc;text-decoration:none;">{title}</a>
      </h2>

      <!-- Authors & Date -->
      <div style="color:#94a3b8;font-size:13px;margin-bottom:18px;font-weight:500;">
        {authors} &nbsp;·&nbsp; {date} &nbsp;·&nbsp; <span style="color:#38bdf8;">{source}</span>
      </div>

      <!-- Abstract -->
      <p style="color:#cbd5e1;font-size:14px;line-height:1.7;margin:0 0 20px 0;border-left:3px solid #334155;padding-left:14px;">
        {abstract}{"..." if len(discovery.get("abstract",""))>500 else ""}
      </p>

      <!-- Ranking Explanation -->
      <div style="background:#020617;border:1px solid #1e293b;border-radius:12px;padding:16px;margin-bottom:16px;">
        <div style="color:#64748b;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;font-weight:700;">AI Ranking Rationale</div>
        <table style="width:100%;border-collapse:collapse;">
          {expl_html}
        </table>
      </div>

      <!-- Cross-disciplinary -->
      {f'<div style="color:#64748b;font-size:10px;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;font-weight:700;margin-top:16px;">⚡ Cross-Disciplinary Architecture</div>' if cross else ""}
      {cross_domain_tags(cross)}

      <!-- Action Buttons -->
      <div style="margin-top:24px;padding-top:16px;border-top:1px solid #1e293b;">
        <a href="{url}" style="background:linear-gradient(135deg, #2563eb, #4f46e5);color:#fff;padding:8px 20px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;display:inline-block;box-shadow: 0 4px 10px rgba(37,99,235,0.3);">🔗 Read Source</a>
        {pdf_btn}
      </div>

    </div>"""


def emerging_trend_item(topic: str, desc: str) -> str:
    return f"""
    <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:16px;">
      <span style="color:#38bdf8;font-size:16px;min-width:20px;text-shadow:0 0 8px rgba(56,189,248,0.5);">◈</span>
      <div>
        <div style="color:#f8fafc;font-size:14px;font-weight:700;">{html_lib.escape(topic)}</div>
        <div style="color:#94a3b8;font-size:13px;margin-top:2px;">{html_lib.escape(desc)}</div>
      </div>
    </div>"""


def build_email_html(papers: list[dict], date_str: str, emerging_trends: list[dict] = None, subscriber_email: str = "") -> str:
    """Build the complete HTML email from ranked papers."""
    today = datetime.date.today().strftime("%A, %B %d, %Y")
    total = len(papers)

    wildcard = papers[-1] if total > 1 else None
    main_papers = papers[:-1] if wildcard else papers

    domains_covered = len(set(p.get("domain","") for p in papers))
    sources_covered = len(set(p.get("source","") for p in papers))
    avg_score = sum(p.get("scores",{}).get("composite",0) for p in max(total, 1)) if total else 0.0

    cards_html = "\n".join(paper_card(i+1, p) for i, p in enumerate(main_papers))

    wildcard_html = ""
    if wildcard:
        wc_title  = html_lib.escape(wildcard.get("title",""))
        wc_abs    = html_lib.escape((wildcard.get("abstract",""))[:400])
        wc_url    = wildcard.get("url","#")
        wc_domain = wildcard.get("domain","")
        wildcard_html = f"""
        <div style="background:linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);border:1px solid #312e81;border-radius:16px;padding:28px;margin-bottom:24px;box-shadow: 0 0 20px rgba(79,70,229,0.1);">
          <div style="color:#a78bfa;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;font-weight:800;">🎲 Wildcard Discovery</div>
          <div style="margin-bottom:12px;">{domain_badge(wc_domain)}</div>
          <h3 style="color:#f8fafc;font-size:18px;margin:0 0 12px 0;font-weight:700;">
            <a href="{wc_url}" style="color:#f8fafc;text-decoration:none;">{wc_title}</a>
          </h3>
          <p style="color:#cbd5e1;font-size:14px;line-height:1.6;margin:0 0 16px 0;">{wc_abs}{"..." if len(wildcard.get("abstract",""))>400 else ""}</p>
          <div style="color:#94a3b8;font-size:12px;font-style:italic;border-left:2px solid #4f46e5;padding-left:10px;">Why this matters: Cross-disciplinary insights often emerge from adjacent fields.</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Noetica Intelligence — {today}</title>
</head>
<body style="margin:0;padding:0;background-color:#020617;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,Cantarell,sans-serif;-webkit-font-smoothing:antialiased;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#020617;">
    <tr><td align="center" style="padding:40px 20px;">

      <table width="700" cellpadding="0" cellspacing="0" style="max-width:700px;width:100%;">
        <tr><td>

          <!-- ══ HEADER ══ -->
          <div style="background:linear-gradient(180deg, #0f172a 0%, #020617 100%);border:1px solid #1e293b;border-radius:24px;padding:48px 40px;margin-bottom:32px;text-align:center;box-shadow:0 20px 40px -10px rgba(0,0,0,0.5);">
            <div style="display:inline-block;width:64px;height:64px;border-radius:16px;background:linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);margin-bottom:20px;box-shadow:0 0 20px rgba(139,92,246,0.3);position:relative;">
               <!-- Geometric Logo Representation -->
               <div style="position:absolute;top:16px;left:16px;right:16px;bottom:16px;border:2px solid #fff;border-radius:50%;opacity:0.8;"></div>
               <div style="position:absolute;top:24px;left:24px;right:24px;bottom:24px;background:#fff;border-radius:50%;"></div>
            </div>
            
            <div style="font-size:11px;letter-spacing:4px;color:#64748b;text-transform:uppercase;margin-bottom:12px;font-weight:800;">Noetica Intelligence</div>
            <h1 style="margin:0 0 12px 0;font-size:36px;font-weight:800;color:#f8fafc;letter-spacing:-1px;">
              Daily Briefing
            </h1>
            <p style="margin:0;color:#94a3b8;font-size:15px;font-weight:500;">{today}</p>
            
            <div style="margin-top:40px;padding-top:28px;border-top:1px solid #1e293b;display:flex;justify-content:center;gap:36px;">
              <div style="text-align:center;">
                <div style="color:#f8fafc;font-size:28px;font-weight:800;">{total}</div>
                <div style="color:#64748b;font-size:10px;letter-spacing:1px;font-weight:700;margin-top:6px;">PAPERS</div>
              </div>
              <div style="color:#1e293b;font-size:28px;">|</div>
              <div style="text-align:center;">
                <div style="color:#f8fafc;font-size:28px;font-weight:800;">{domains_covered}</div>
                <div style="color:#64748b;font-size:10px;letter-spacing:1px;font-weight:700;margin-top:6px;">DOMAINS</div>
              </div>
              <div style="color:#1e293b;font-size:28px;">|</div>
              <div style="text-align:center;">
                <div style="color:#f8fafc;font-size:28px;font-weight:800;">{avg_score:.1f}</div>
                <div style="color:#64748b;font-size:10px;letter-spacing:1px;font-weight:700;margin-top:6px;">AVG SCORE</div>
              </div>
            </div>
          </div>

          <!-- ══ SECTION LABEL ══ -->
          <div style="color:#94a3b8;font-size:12px;letter-spacing:3px;text-transform:uppercase;margin-bottom:24px;padding:0 8px;font-weight:800;display:flex;align-items:center;gap:12px;">
            <div style="height:1px;background:#1e293b;flex:1;"></div>
            <span>High-Impact Discoveries</span>
            <div style="height:1px;background:#1e293b;flex:1;"></div>
          </div>

          <!-- ══ PAPER CARDS ══ -->
          {cards_html}

          <!-- ══ WILDCARD ══ -->
          {wildcard_html}

          <!-- ══ EMERGING TRENDS ══ -->
          <div style="background:#0f172a;border:1px solid #1e293b;border-radius:16px;padding:32px;margin-top:16px;margin-bottom:32px;box-shadow:0 10px 20px rgba(0,0,0,0.3);">
            <div style="color:#38bdf8;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:24px;font-weight:800;display:flex;align-items:center;gap:8px;">
              <span>📈 Emerging Trends Detected</span>
            </div>
            {_build_trends_html(emerging_trends)}
          </div>

          <!-- ══ FOOTER ══ -->
          <div style="text-align:center;padding:40px 24px;color:#64748b;font-size:13px;border-top:1px solid #1e293b;">
            {_build_footer_feedback(subscriber_email)}
            <p style="margin:32px 0 8px 0;font-weight:700;color:#94a3b8;letter-spacing:1px;text-transform:uppercase;font-size:11px;">Noetica Intelligence System</p>
            <p style="margin:0 0 16px 0;font-size:12px;">Powered by arXiv · PubMed · bioRxiv · Semantic Scholar</p>
            <p style="margin:0;font-size:11px;color:#475569;font-style:italic;">This is an automated intelligence briefing. Do not forward without authorization.</p>
          </div>

        </td></tr>
      </table>

    </td></tr>
  </table>
</body>
</html>"""


def _build_trends_html(trends: list[dict] | None) -> str:
    if not trends:
        defaults = [
            ("AI-Assisted Science", "LLMs generating and verifying novel hypotheses"),
            ("Quantum-Classical Hybrid", "Near-term quantum advantage in optimization"),
            ("Circadian Pharmacology", "Timing-dependent drug efficacy across oncology trials"),
            ("Foundation Models for Biology", "Protein/DNA/RNA language models converging"),
        ]
        return "\n".join(emerging_trend_item(t, d) for t, d in defaults)

    items = []
    for t in trends[:6]:
        icon = "🔥" if t.get("type") == "convergence" else "📈"
        name = t.get("name", "")
        desc = t.get("description", "")
        items.append(emerging_trend_item(f"{icon} {name}", desc))
    return "\n".join(items)


def _build_footer_feedback(email: str) -> str:
    try:
        from feedback import build_global_feedback_footer_html
        return build_global_feedback_footer_html(email)
    except Exception:
        return (
            '<div style="margin-bottom:24px;">'
            '<p style="margin:0 0 16px 0;font-weight:600;color:#cbd5e1;">Rate this intelligence briefing:</p>'
            '<div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;">'
            '<a href="#" style="background:#1e293b;border:1px solid #334155;color:#38bdf8;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600;transition:all 0.2s;">Excellent</a>'
            '<a href="#" style="background:#1e293b;border:1px solid #334155;color:#cbd5e1;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600;transition:all 0.2s;">Average</a>'
            '<a href="#" style="background:#1e293b;border:1px solid #334155;color:#ef4444;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600;transition:all 0.2s;">Poor</a>'
            '</div>'
            '</div>'
        )


def build_email_subject(papers: list[dict], date_str: str) -> str:
    today = datetime.date.today().strftime("%b %d")
    top = papers[0] if papers else None
    if top:
        short_title = top.get("title","")[:50]
        score = top.get("scores",{}).get("composite",0)
        return f"🔬 [{today}] [{score:.1f}/10] {short_title}... + {len(papers)-1} breakthroughs"
    return f"🔬 Noetica Intelligence Briefing — {today}"


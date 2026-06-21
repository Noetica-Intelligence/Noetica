"""
Scientific Intelligence Engine — Email Builder
Generates a premium dark/light mode HTML email digest with scoring cards,
cross-domain connections, and wildcard discovery section.
"""

import re
import datetime
import html as html_lib

# ─────────────────────────────────────────────
# DOMAIN → COLOR MAPPING (Curated Premium Colors)
# ─────────────────────────────────────────────

DOMAIN_COLORS = {
    "Theoretical Physics":   ("#6366f1", "#e0e7ff"),  # Indigo
    "Experimental Physics":  ("#4f46e5", "#e0e7ff"),
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
    "Molecular Dynamics":    ("#6366f1", "#e0e7ff"),
    "Philosophy":            ("#d97706", "#fef3c7"),
    "Economics":             ("#059669", "#d1fae5"),
    "Psychology":            ("#db2777", "#fce7f3"),
    "Computer Science":      ("#2563eb", "#dbeafe"),
    "Mathematics":           ("#059669", "#d1fae5"),
    "Physics":               ("#6366f1", "#e0e7ff"),
    "Biology":               ("#16a34a", "#dcfce7"),
    "Medicine":              ("#db2777", "#fce7f3"),
    "Engineering":           ("#ea580c", "#ffedd5"),
    "default":               ("#64748b", "#f8fafc"),
}

# ─────────────────────────────────────────────
# PRE-PROCESSORS
# ─────────────────────────────────────────────

def latex_to_unicode(text: str) -> str:
    """Safely convert common LaTeX symbols to Unicode for email rendering."""
    if not text:
        return ""
    
    replacements = {
        r"$_2$": "₂", r"$_3$": "₃", r"$_4$": "₄", r"$_5$": "₅",
        r"$^2$": "²", r"$^3$": "³", r"$^4$": "⁴",
        r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
        r"\ell": "ℓ", r"\mu": "μ", r"\pi": "π", r"\sigma": "σ",
        r"\theta": "θ", r"\infty": "∞",
        r"\epsilon": "ε", r"\Omega": "Ω", r"\Delta": "Δ",
        r"\to": "→", r"\nu": "ν",
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
        
    # Strip remaining $ signs used as math mode delimiters (e.g., $x$, $\ell\ell\nu\nu$, $(p=1)$)
    # We remove any $ that wraps text, to clean up the abstract.
    text = re.sub(r'\$([^\$]+)\$', r'\1', text)
    
    return text


def domain_badge(domain: str) -> str:
    fg, bg = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["default"])
    esc = html_lib.escape(domain)
    # Inline style fallback for badges
    return f'<span class="badge" style="background:{bg};color:{fg};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;letter-spacing:0.5px;border:1px solid {fg}40;">{esc}</span>'


def cross_domain_tags(domains: list[str]) -> str:
    if not domains:
        return ""
    tags = " ".join(
        f'<span class="cross-tag" style="background:#f8fafc;color:#64748b;border:1px solid #cbd5e1;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;display:inline-block;margin-right:4px;margin-bottom:4px;">'
        f'→ {html_lib.escape(d)}</span>'
        for d in domains[:4]
    )
    return f'<div style="margin-top:6px;">{tags}</div>'


def score_color_class(score: int) -> str:
    if score >= 85: return "score-high"
    if score >= 75: return "score-med"
    return "score-low"


def paper_card(rank: int, discovery: dict) -> str:
    """Generate a full discovery card HTML block with premium hierarchy."""
    title    = html_lib.escape(latex_to_unicode(discovery.get("title", "Untitled")))
    raw_abs  = latex_to_unicode(discovery.get("abstract", ""))
    abstract = html_lib.escape(raw_abs[:220]) + ("..." if len(raw_abs) > 220 else "")
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
    explanation = html_lib.escape(discovery.get("explanation", "Emerging signal detected."))
    status   = discovery.get("status", "Emerging Signal")

    composite_100 = scores.get("composite", 65)
    s_class = score_color_class(composite_100)

    # Status Color Logic
    status_bg = "#f0fdf4"
    status_fg = "#16a34a"
    if status == "Breakthrough Signal":
        status_bg = "#fef2f2"
        status_fg = "#dc2626"
    elif status == "Strong Signal":
        status_bg = "#fffbeb"
        status_fg = "#d97706"

    pdf_btn = ""
    if pdf_url:
        pdf_btn = f' &nbsp;<a href="{pdf_url}" class="btn-pdf" style="background:#f1f5f9;border:1px solid #cbd5e1;color:#475569;padding:8px 16px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:600;display:inline-block;">📄 PDF</a>'

    return f"""
    <div class="card" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px;margin-bottom:24px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);">

      <!-- Header Row (Table used for 100% email client compatibility) -->
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:16px;">
        <tr>
          <td align="left" valign="middle">
            {domain_badge(domain)}
            <span style="display:inline-block; width:8px;"></span>
            <span class="status-badge" style="background:{status_bg};border:1px solid {status_fg}40;color:{status_fg};padding:3px 8px;border-radius:6px;font-size:10px;text-transform:uppercase;letter-spacing:1px;font-weight:800;display:inline-block;">{status}</span>
          </td>
          <td align="right" valign="middle">
            <div class="{s_class} score-display" style="font-size:24px;font-weight:800;line-height:1;margin-bottom:4px;">{composite_100}<span style="font-size:14px;opacity:0.6;font-weight:600;">/100</span></div>
            <div class="score-label" style="color:#94a3b8;font-size:10px;letter-spacing:1px;font-weight:700;">SIGNAL</div>
          </td>
        </tr>
      </table>

      <!-- Title -->
      <h2 style="margin:0 0 10px 0;font-size:22px;font-weight:800;line-height:1.3;letter-spacing:-0.5px;">
        <a href="{url}" class="card-title" style="color:#0f172a;text-decoration:none;">{title}</a>
      </h2>

      <!-- Authors & Source -->
      <div class="meta-text" style="color:#64748b;font-size:13px;margin-bottom:20px;font-weight:500;">
        {authors} &nbsp;·&nbsp; {date} &nbsp;·&nbsp; <span style="color:#0284c7;font-weight:600;">{source}</span>
      </div>

      <!-- Why it matters (Narrative AI Rationale) -->
      <div class="rationale-box" style="background:#f8fafc;border-left:4px solid #3b82f6;padding:16px 20px;margin-bottom:16px;border-radius:0 8px 8px 0;">
        <div style="color:#3b82f6;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">⚡ Why Noetica Flagged This</div>
        <div style="color:#334155;font-size:14px;line-height:1.6;font-weight:500;">
          {explanation}
        </div>
      </div>

      <!-- Truncated Abstract -->
      <p class="abstract-text" style="color:#64748b;font-size:13px;line-height:1.6;margin:0 0 12px 0;font-style:italic;">
        "{abstract}"
      </p>

      <!-- Cross-disciplinary -->
      {f'<div class="cross-label" style="color:#94a3b8;font-size:10px;letter-spacing:1px;text-transform:uppercase;margin-bottom:2px;font-weight:700;">Cross-Disciplinary Architecture</div>' if cross else ""}
      {cross_domain_tags(cross)}

      <!-- Action Buttons -->
      <div style="margin-top:20px;padding-top:16px;border-top:1px solid #f1f5f9;">
        <a href="{url}" class="btn-primary" style="background:#0f172a;color:#ffffff;padding:8px 20px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;display:inline-block;">Read Publication</a>
        {pdf_btn}
      </div>

    </div>"""


def build_email_html(papers: list[dict], date_str: str, emerging_trends: list[dict] = None, subscriber_email: str = "") -> str:
    today = datetime.date.today().strftime("%A, %B %d, %Y")
    total = len(papers)

    wildcard = papers[-1] if total > 1 else None
    main_papers = papers[:-1] if wildcard else papers

    cards_html = "\n".join(paper_card(i+1, p) for i, p in enumerate(main_papers))

    wildcard_html = ""
    if wildcard:
        wc_title  = html_lib.escape(latex_to_unicode(wildcard.get("title","")))
        wc_abs    = html_lib.escape(latex_to_unicode((wildcard.get("abstract",""))[:250]))
        wc_url    = wildcard.get("url","#")
        wc_domain = wildcard.get("domain","")
        wc_expl   = html_lib.escape(wildcard.get("explanation", "Detected unusual cross-domain intersection."))
        wildcard_html = f"""
        <div class="wildcard-card" style="background:linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);border:1px solid #ddd6fe;border-radius:16px;padding:32px;margin-bottom:24px;">
          <div style="color:#7c3aed;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;font-weight:800;">
            <span style="font-size:16px;vertical-align:middle;">⚡</span> <span style="vertical-align:middle;">OUTSIDE YOUR FIELD</span>
          </div>
          <div style="margin-bottom:12px;">{domain_badge(wc_domain)}</div>
          <h3 style="color:#4c1d95;font-size:20px;margin:0 0 12px 0;font-weight:800;line-height:1.3;">
            <a href="{wc_url}" style="color:#4c1d95;text-decoration:none;">{wc_title}</a>
          </h3>
          <div style="background:#ffffff;border-radius:8px;padding:16px;margin-bottom:16px;border:1px solid #e2e8f0;">
             <div style="color:#7c3aed;font-size:11px;font-weight:800;text-transform:uppercase;margin-bottom:4px;">Why you're seeing this</div>
             <div style="color:#334155;font-size:13px;line-height:1.5;font-weight:500;">
               {wc_expl} Cross-disciplinary breakthroughs often emerge from unexpected domains.
             </div>
          </div>
          <p style="color:#6b7280;font-size:13px;line-height:1.6;margin:0 0 16px 0;font-style:italic;">"{wc_abs}..."</p>
          <a href="{wc_url}" style="color:#7c3aed;font-weight:700;font-size:13px;text-decoration:none;">Explore Wildcard →</a>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Noetica Intelligence — {today}</title>
<style>
  body {{ margin:0; padding:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,Cantarell,sans-serif; -webkit-font-smoothing:antialiased; background-color:#f8fafc; }}
  
  /* Dark Mode Support via Media Query */
  @media (prefers-color-scheme: dark) {{
    body {{ background-color: #000000 !important; }}
    .main-wrapper {{ background-color: #000000 !important; }}
    
    .header-box {{ background: #0f172a !important; border-color: #1e293b !important; box-shadow: 0 20px 40px -10px rgba(0,0,0,0.8) !important; }}
    .header-title {{ color: #ffffff !important; }}
    .header-metric {{ color: #ffffff !important; }}
    
    .card {{ background: #0a0a0a !important; border-color: #1e293b !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5) !important; }}
    .card-title {{ color: #f8fafc !important; }}
    .meta-text {{ color: #94a3b8 !important; }}
    
    .rationale-box {{ background: #020617 !important; border-left-color: #4f46e5 !important; border: 1px solid #1e293b; border-left: 4px solid #4f46e5; }}
    .rationale-box div {{ color: #cbd5e1 !important; }}
    .rationale-box div:first-child {{ color: #818cf8 !important; }}
    
    .abstract-text {{ color: #94a3b8 !important; }}
    .cross-tag {{ background: #0f172a !important; border-color: #334155 !important; color: #cbd5e1 !important; }}
    .btn-primary {{ background: #ffffff !important; color: #000000 !important; }}
    .btn-pdf {{ background: #0f172a !important; border-color: #334155 !important; color: #cbd5e1 !important; }}
    
    .wildcard-card {{ background: #0f172a !important; border-color: #312e81 !important; }}
    .wildcard-card h3 a {{ color: #e0e7ff !important; }}
    .wildcard-card > div:nth-of-type(3) {{ background: #020617 !important; border-color: #1e293b !important; }}
    .wildcard-card > div:nth-of-type(3) div {{ color: #cbd5e1 !important; }}
    .wildcard-card > div:nth-of-type(3) div:first-child {{ color: #a78bfa !important; }}
    
    .score-high {{ color: #10b981 !important; text-shadow: 0 0 10px rgba(16,185,129,0.3) !important; }}
    .score-med {{ color: #f59e0b !important; text-shadow: 0 0 10px rgba(245,158,11,0.3) !important; }}
    .score-low {{ color: #ef4444 !important; text-shadow: 0 0 10px rgba(239,68,68,0.3) !important; }}
  }}

  .score-high {{ color: #059669; }}
  .score-med {{ color: #d97706; }}
  .score-low {{ color: #dc2626; }}
</style>
</head>
<body class="main-wrapper">
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr><td align="center" style="padding:40px 20px;">

      <table width="700" cellpadding="0" cellspacing="0" border="0" style="max-width:700px;width:100%;">
        <tr><td>

          <!-- ══ HEADER ══ -->
          <div class="header-box" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:24px;padding:48px 40px;margin-bottom:40px;text-align:center;box-shadow:0 10px 30px -10px rgba(0,0,0,0.05);">
            
            <!-- Robust image logo hosted from GitHub, replacing broken pure CSS shape -->
            <img src="https://raw.githubusercontent.com/Noetica-Intelligence/Noetica/main/assets/logo.png" alt="Noetica Logo" width="80" height="80" style="display:block;margin:0 auto;margin-bottom:24px;border-radius:20px;border:1px solid #e2e8f0;" />
            
            <div style="font-size:11px;letter-spacing:4px;color:#64748b;text-transform:uppercase;margin-bottom:12px;font-weight:800;">Noetica Intelligence</div>
            <h1 class="header-title" style="margin:0 0 12px 0;font-size:36px;font-weight:800;color:#0f172a;letter-spacing:-1px;">
              Intelligence Briefing
            </h1>
            <p style="margin:0;color:#64748b;font-size:15px;font-weight:500;">{today}</p>
          </div>

          <!-- ══ SECTION LABEL ══ -->
          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
            <tr>
              <td width="35%" style="border-top:1px solid #e2e8f0;"></td>
              <td width="30%" align="center" style="color:#94a3b8;font-size:11px;letter-spacing:2px;text-transform:uppercase;font-weight:800;padding:0 10px;">
                Detected Signals
              </td>
              <td width="35%" style="border-top:1px solid #e2e8f0;"></td>
            </tr>
          </table>

          <!-- ══ PAPER CARDS ══ -->
          {cards_html}

          <!-- ══ WILDCARD ══ -->
          {wildcard_html}

          <!-- ══ FOOTER ══ -->
          <div style="text-align:center;padding:40px 24px;color:#64748b;font-size:13px;border-top:1px solid #e2e8f0;margin-top:40px;">
            <p style="margin:0 0 8px 0;font-weight:800;color:#94a3b8;letter-spacing:1px;text-transform:uppercase;font-size:11px;">Noetica Intelligence Network</p>
            <p style="margin:0 0 16px 0;font-size:12px;">Powered by arXiv · PubMed · Semantic Scholar</p>
            <p style="margin:0;font-size:11px;color:#94a3b8;font-style:italic;">This is an automated intelligence briefing. Do not forward without authorization.</p>
          </div>

        </td></tr>
      </table>

    </td></tr>
  </table>
</body>
</html>"""


def build_email_subject(papers: list[dict], date_str: str) -> str:
    """Create a premium intelligence-style subject line."""
    if not papers:
        return "Noetica Daily Intelligence | No Significant Signals Detected"
        
    domains = list(set(p.get("domain", "") for p in papers if p.get("domain")))
    domain_str = "Science & Tech"
    if len(domains) >= 2:
        domain_str = f"{domains[0]} & {domains[1]}"
    elif len(domains) == 1:
        domain_str = domains[0]
        
    return f"Noetica Intelligence Brief | {len(papers)} Emerging Signals in {domain_str}"

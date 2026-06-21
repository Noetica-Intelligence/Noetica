"""
Scientific Intelligence Engine — Email Builder
Generates a premium dark/light mode HTML email digest with an Insight-First architecture.
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
        
    text = re.sub(r'\$([^\$]+)\$', r'\1', text)
    return text


def domain_badge(domain: str) -> str:
    fg, bg = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["default"])
    esc = html_lib.escape(domain)
    return f'<span class="badge" style="background:{bg};color:{fg};padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;letter-spacing:0.5px;border:1px solid {fg}40;">{esc}</span>'


def paper_card(rank: int, discovery: dict) -> str:
    """Generate a full discovery card HTML block with an Insight-First hierarchy."""
    title    = html_lib.escape(latex_to_unicode(discovery.get("title", "Untitled")))
    raw_abs  = latex_to_unicode(discovery.get("abstract", ""))
    abstract = html_lib.escape(raw_abs[:300]) + ("..." if len(raw_abs) > 300 else "")
    authors  = ", ".join(html_lib.escape(a) for a in (discovery.get("authors") or [])[:3])
    if len(discovery.get("authors") or []) > 3:
        authors += " et al."
    date     = discovery.get("date", "")[:10]
    source   = html_lib.escape(discovery.get("source", ""))
    url      = discovery.get("url", "#")
    pdf_url  = discovery.get("pdf_url", "")
    domain   = discovery.get("domain", "Other")
    scores   = discovery.get("scores", {})
    status   = discovery.get("status", "Emerging Signal")
    
    # New Architectural Fields
    strat_imp = html_lib.escape(discovery.get("strategic_implication", "Incremental advancement detected."))
    kg_edge   = html_lib.escape(discovery.get("knowledge_graph_edge", ""))

    composite_100 = scores.get("composite", 65)

    pdf_btn = ""
    if pdf_url:
        pdf_btn = f' &nbsp;<a href="{pdf_url}" class="btn-pdf" style="background:#f1f5f9;border:1px solid #cbd5e1;color:#475569;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;display:inline-block;">PDF</a>'

    kg_html = ""
    if kg_edge:
        kg_html = f"""
        <div style="margin-top:16px;">
           <div style="font-size:10px;color:#64748b;text-transform:uppercase;font-weight:800;letter-spacing:1px;margin-bottom:6px;">Knowledge Graph Vector</div>
           <div class="kg-box" style="font-size:13px;color:#475569;background:#ffffff;border:1px dashed #cbd5e1;padding:12px;border-radius:8px;font-weight:500;">
              ⮑ {kg_edge}
           </div>
        </div>
        """

    return f"""
    <div class="card" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;padding:28px;margin-bottom:24px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);">

      <!-- Subtle Telemetry Row -->
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:16px;">
        <tr>
          <td align="left" valign="middle">
            <span class="net-score" style="background:#f8fafc;color:#475569;border:1px solid #e2e8f0;padding:4px 8px;border-radius:6px;font-size:10px;font-weight:800;letter-spacing:1px;margin-right:8px;">NET:{composite_100}</span>
            {domain_badge(domain)}
          </td>
          <td align="right" valign="middle">
            <span style="font-size:10px;color:#94a3b8;font-weight:800;text-transform:uppercase;letter-spacing:1px;">{status}</span>
          </td>
        </tr>
      </table>

      <!-- Title & Authors -->
      <h2 style="margin:0 0 8px 0;font-size:20px;font-weight:800;line-height:1.4;letter-spacing:-0.5px;">
        <a href="{url}" class="card-title" style="color:#0f172a;text-decoration:none;">{title}</a>
      </h2>
      <div class="meta-text" style="color:#64748b;font-size:13px;margin-bottom:24px;font-weight:500;">
        {authors} &nbsp;·&nbsp; <span style="color:#0284c7;font-weight:600;">{source}</span>
      </div>

      <!-- Strategic Implication (The Core Insight) -->
      <div class="rationale-box" style="background:#f8fafc; border-left:3px solid #0f172a; padding:16px; border-radius:0 8px 8px 0;">
         <div class="rationale-title" style="font-size:10px;color:#0f172a;text-transform:uppercase;font-weight:800;letter-spacing:1.5px;margin-bottom:8px;">Strategic Implication</div>
         <div class="rationale-text" style="font-size:14px;color:#334155;line-height:1.6;font-weight:500;">
            {strat_imp}
         </div>
      </div>

      <!-- Knowledge Graph Connections -->
      {kg_html}

      <!-- Abstract (Demoted) -->
      <div class="abstract-text" style="margin-top:20px; font-size:12px; color:#94a3b8; font-style:italic; line-height:1.6; border-top:1px solid #f1f5f9; padding-top:16px;">
         Reference: "{abstract}"
      </div>

      <!-- Action Buttons -->
      <div style="margin-top:20px;">
        <a href="{url}" class="btn-primary" style="background:#0f172a;color:#ffffff;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;display:inline-block;text-transform:uppercase;letter-spacing:0.5px;">View Source</a>
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
        wc_url    = wildcard.get("url","#")
        wc_domain = wildcard.get("domain","")
        wc_strat  = html_lib.escape(wildcard.get("strategic_implication", "Detected anomaly with cross-domain potential."))
        wc_kg     = html_lib.escape(wildcard.get("knowledge_graph_edge", "Convergence vector unclear."))
        
        wildcard_html = f"""
        <div class="wildcard-card" style="background:#0f172a;border:1px solid #1e293b;border-radius:16px;padding:32px;margin-bottom:24px;box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;">
             <tr>
               <td align="left">
                 <div style="color:#ef4444;font-size:11px;letter-spacing:2px;text-transform:uppercase;font-weight:800;">
                   <span style="font-size:14px;vertical-align:middle;">⚠️</span> <span style="vertical-align:middle;">Anomaly Detected</span>
                 </div>
               </td>
               <td align="right">
                 {domain_badge(wc_domain)}
               </td>
             </tr>
          </table>

          <h3 style="color:#f8fafc;font-size:22px;margin:0 0 16px 0;font-weight:800;line-height:1.4;">
            <a href="{wc_url}" style="color:#f8fafc;text-decoration:none;">{wc_title}</a>
          </h3>
          
          <div style="background:#020617;border:1px solid #1e293b;border-radius:8px;padding:16px;margin-bottom:16px;">
             <div style="color:#f87171;font-size:10px;font-weight:800;text-transform:uppercase;margin-bottom:8px;letter-spacing:1px;">Convergence Potential</div>
             <div style="color:#cbd5e1;font-size:14px;line-height:1.6;font-weight:500;">
               {wc_strat} {wc_kg}
             </div>
          </div>
          
          <a href="{wc_url}" style="color:#ef4444;font-weight:700;font-size:12px;text-decoration:none;text-transform:uppercase;letter-spacing:1px;">Analyze Anomaly →</a>
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
    .header-subtitle {{ color: #94a3b8 !important; }}
    
    .card {{ background: #0a0a0a !important; border-color: #1e293b !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5) !important; }}
    .card-title {{ color: #f8fafc !important; }}
    .meta-text {{ color: #64748b !important; }}
    .net-score {{ background: #020617 !important; border-color: #1e293b !important; color: #94a3b8 !important; }}
    
    .rationale-box {{ background: #020617 !important; border-color: #1e293b !important; border-left-color: #e2e8f0 !important; }}
    .rationale-title {{ color: #e2e8f0 !important; }}
    .rationale-text {{ color: #cbd5e1 !important; }}
    
    .kg-box {{ background: #0a0a0a !important; border-color: #334155 !important; color: #94a3b8 !important; }}
    
    .abstract-text {{ color: #475569 !important; border-top-color: #1e293b !important; }}
    .btn-primary {{ background: #ffffff !important; color: #000000 !important; }}
    .btn-pdf {{ background: #0f172a !important; border-color: #334155 !important; color: #cbd5e1 !important; }}
  }}
</style>
</head>
<body class="main-wrapper">
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr><td align="center" style="padding:40px 20px;">

      <table width="700" cellpadding="0" cellspacing="0" border="0" style="max-width:700px;width:100%;">
        <tr><td>

          <!-- ══ HEADER (NETWORK TELEMETRY) ══ -->
          <div class="header-box" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:24px;padding:48px 40px;margin-bottom:40px;text-align:center;box-shadow:0 10px 30px -10px rgba(0,0,0,0.05);">
            
            <img src="cid:logo.png" alt="Noetica Logo" width="64" height="64" style="display:block;margin:0 auto;margin-bottom:24px;border-radius:16px;border:1px solid #e2e8f0;" />
            
            <h1 class="header-title" style="margin:0 0 8px 0;font-size:32px;font-weight:800;color:#0f172a;letter-spacing:-1px;">
              Intelligence Briefing
            </h1>
            <p class="header-subtitle" style="margin:0 0 32px 0;color:#64748b;font-size:14px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">
              T-24 Hour Network Telemetry · {today}
            </p>

            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                 <td align="center" width="33%">
                   <div style="font-size:28px;font-weight:800;color:#0f172a;line-height:1;">4,102</div>
                   <div style="font-size:10px;color:#94a3b8;text-transform:uppercase;font-weight:700;letter-spacing:1px;margin-top:8px;">Signals Scanned</div>
                 </td>
                 <td align="center" width="33%" style="border-left:1px solid #e2e8f0;border-right:1px solid #e2e8f0;">
                   <div style="font-size:28px;font-weight:800;color:#059669;line-height:1;">{total}</div>
                   <div style="font-size:10px;color:#94a3b8;text-transform:uppercase;font-weight:700;letter-spacing:1px;margin-top:8px;">Emerging Vectors</div>
                 </td>
                 <td align="center" width="33%">
                   <div style="font-size:28px;font-weight:800;color:#ef4444;line-height:1;">{1 if wildcard else 0}</div>
                   <div style="font-size:10px;color:#94a3b8;text-transform:uppercase;font-weight:700;letter-spacing:1px;margin-top:8px;">Anomalies</div>
                 </td>
              </tr>
            </table>
          </div>

          <!-- ══ PAPER CARDS ══ -->
          {cards_html}

          <!-- ══ WILDCARD / ANOMALY ══ -->
          {wildcard_html}

          <!-- ══ FOOTER ══ -->
          <div style="text-align:center;padding:40px 24px;color:#64748b;font-size:13px;border-top:1px solid #e2e8f0;margin-top:40px;">
            <p style="margin:0 0 8px 0;font-weight:800;color:#94a3b8;letter-spacing:2px;text-transform:uppercase;font-size:11px;">Noetica Intelligence Network</p>
            <p style="margin:0;font-size:11px;color:#94a3b8;font-style:italic;">This is a classified intelligence briefing. Do not distribute without authorization.</p>
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

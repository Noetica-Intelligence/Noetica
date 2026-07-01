import os
import re
import io

css_path = 'index.css'
with io.open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix toc-item.active
css = re.sub(
    r'\.toc-item\.active \{[^\}]+\}',
    '.toc-item.active {\n    background: rgba(59, 130, 246, 0.1);\n    box-shadow: none;\n    border-radius: 8px;\n    border-left: none;\n    padding-left: 1rem;\n    font-weight: 700;\n    color: var(--color-brand-blue);\n}',
    css
)

# Fix sidebar padding for pill
css = css.replace('.toc-item {\n    padding: 0.6rem 1rem;\n    margin: 0.2rem 1.5rem;', '.toc-item {\n    padding: 0.6rem 1rem;\n    margin: 0.2rem 1rem;')

# Fix pre-footer alignment (the 4 columns were left aligned because grid items take full space)
# We can just center the content or give the grid a max-width and center it
if 'justify-content: center;' not in css:
    css = css.replace('grid-template-columns: repeat(4, 1fr);\n    }', 'grid-template-columns: repeat(4, 1fr);\n        gap: 2rem;\n    }')

# Waitlist Banner - make it compact
css = css.replace('padding: 2.5rem;\n    display: flex;', 'padding: 1.5rem 2rem;\n    display: flex;')
css = css.replace('margin-top: 4rem;', 'margin-top: 2rem;')
css = css.replace('gap: 2rem;', 'gap: 1rem;')

# Waitlist button animation
waitlist_btn_anim = """
.btn-waitlist {
    background: linear-gradient(135deg, var(--color-brand-blue), #6366f1);
    color: white;
    padding: 0.8rem 1.8rem;
    border-radius: 30px;
    text-decoration: none;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    position: relative;
    overflow: hidden;
    border: none;
}
.btn-waitlist::after {
    content: '';
    position: absolute;
    top: 0; left: -100%; width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: btnShine 3s infinite;
}
@keyframes btnShine {
    0% { left: -100%; }
    20% { left: 200%; }
    100% { left: 200%; }
}
.btn-waitlist:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
}

.arch-diagram {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 3rem;
    margin: 3rem 0;
    background: var(--color-surface);
    border-radius: 16px;
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    flex-wrap: wrap;
}
.arch-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--color-bg);
    border-radius: 12px;
    border: 1px solid var(--color-border);
    flex: 1;
    min-width: 200px;
}
.arch-node svg { width: 32px; height: 32px; color: var(--color-brand-blue); }
.arch-node span { font-weight: 600; color: var(--color-text-primary); font-size: 1.05rem; }
.arch-node small { color: var(--color-text-muted); font-size: 0.85rem; font-weight: 400; display: block; margin-top: 4px; }
.arch-arrow {
    color: var(--color-text-muted);
    font-size: 1.5rem;
    font-weight: bold;
}
.engine-node {
    border-color: var(--color-brand-blue);
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.1);
}
"""

css = re.sub(r'\.btn-waitlist \{.*?\}', '', css, flags=re.DOTALL)
css = re.sub(r'\.btn-waitlist:hover \{.*?\}', '', css, flags=re.DOTALL)
css += waitlist_btn_anim

with io.open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# Update HTML files
html_files = [
    'architecture.html', 'index.html', 'ingestion.html', 
    'principles.html', 'scoring.html', 'timelines.html'
]

social_links_old = """<div class="footer-socials">
                    <a href="#"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg></a>
                    <a href="#"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg></a>
                    <a href="#"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg></a>
                    <a href="#"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg></a>
                </div>"""

social_links_new = """<div class="footer-socials">
                    <a href="https://github.com/skanishmd" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg></a>
                    <a href="https://www.linkedin.com/in/skanishmd" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg></a>
                    <a href="mailto:skanishmd321@gmail.com"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg></a>
                    <a href="https://www.instagram.com/sk4nishmd" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg></a>
                </div>"""

arch_diagram_html = """
                <div class="arch-diagram reveal-on-scroll">
                    <div class="arch-node">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16c0 1.1.9 2 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/><path d="M14 3v5h5M16 13H8M16 17H8M10 9H8"/></svg>
                        <span>Raw Literature<br><small>Millions of Unstructured Papers</small></span>
                    </div>
                    <div class="arch-arrow">&rarr;</div>
                    <div class="arch-node engine-node">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                        <span>Noetica Engine<br><small>Biomechanical & Signal Validation</small></span>
                    </div>
                    <div class="arch-arrow">&rarr;</div>
                    <div class="arch-node">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                        <span>Verified Pathways<br><small>Actionable Discoveries</small></span>
                    </div>
                </div>
"""

for filename in html_files:
    if not os.path.exists(filename): continue
    with io.open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = content.replace(social_links_old, social_links_new)
    content = content.replace('â†’', '&rarr;')
    content = content.replace('â€”', '&mdash;')
    
    if filename == 'index.html':
        content = re.sub(
            r'<div class="product-preview reveal-on-scroll".*?</div>',
            arch_diagram_html,
            content,
            flags=re.DOTALL
        )
        
    with io.open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

print("Python script complete")

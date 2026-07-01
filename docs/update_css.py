import os
import re

css_path = 'index.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix toc-item.active
css = re.sub(
    r'\.toc-item\.active \{[^\}]+\}',
    '.toc-item.active {\n    background: rgba(59, 130, 246, 0.1);\n    box-shadow: none;\n    border-radius: 8px;\n    padding-left: 1rem;\n    font-weight: 700;\n    color: var(--color-brand-blue);\n}',
    css
)

# Fix sidebar-toc padding for better pill alignment
css = css.replace('.toc-item {\n    padding: 0.6rem 1rem;\n    margin: 0.2rem 1.5rem;', '.toc-item {\n    padding: 0.6rem 1rem;\n    margin: 0.2rem 1rem;')

# Fix pre-footer-grid to center it properly if it wasn't
css = css.replace('grid-template-columns: repeat(4, 1fr);\n}', 'grid-template-columns: repeat(4, 1fr);\n        justify-content: center;\n        justify-items: center;\n}')

# Waitlist Banner - make it compact
css = css.replace('padding: 2.5rem;\n    display: flex;', 'padding: 1.5rem 2rem;\n    display: flex;')
css = css.replace('margin-top: 4rem;', 'margin-top: 3rem;')
css = css.replace('gap: 2rem;', 'gap: 1.5rem;')

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
"""

css = re.sub(r'\.btn-waitlist \{.*?\}', '', css, flags=re.DOTALL)
css = re.sub(r'\.btn-waitlist:hover \{.*?\}', '', css, flags=re.DOTALL)
css += waitlist_btn_anim

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("CSS updated")

import os
import re
import io

html_files = [
    'architecture.html', 'index.html', 'ingestion.html', 
    'principles.html', 'scoring.html', 'timelines.html'
]

sidebar_back_btn = """
        <a href="index.html" class="sidebar-back-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
            <div>
                Back to Noetica Home
                <span class="sidebar-back-desc">Return to main website</span>
            </div>
        </a>
"""

waitlist_banner = """
        <!-- Waitlist / Beta Section -->
        <div class="waitlist-banner reveal-on-scroll" id="beta-registration">
            <div class="waitlist-content">
                <h3>Noetica Closed Beta is Live</h3>
                <p>Join the waitlist to get early access when we open spots.</p>
                <div class="waitlist-features">
                    <div class="waitlist-feature">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                        Limited to first 500 users
                    </div>
                    <div class="waitlist-feature">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        Early access
                    </div>
                    <div class="waitlist-feature">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                        Help shape Noetica
                    </div>
                    <div class="waitlist-feature">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                        No spam. Ever.
                    </div>
                </div>
            </div>
            <div class="waitlist-action">
                <a href="#" class="btn-waitlist">Join the Waitlist &rarr;</a>
                <small>Opens in Google Form</small>
            </div>
        </div>
"""

new_footers = """
    <!-- 4-Column Footer -->
    <div class="pre-footer-wrapper">
        <div class="pre-footer-grid">
            <!-- Col 1 -->
            <div class="footer-col">
                <div class="creator-avatar">SA</div>
                <h4>Sk Anish Md.</h4>
                <p>A Bioinformatics student, developer, and researcher building tools that accelerate scientific discovery through AI, data, and open knowledge.</p>
                <div class="footer-socials">
                    <a href="#"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg></a>
                    <a href="#"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg></a>
                    <a href="#"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg></a>
                    <a href="#"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg></a>
                </div>
            </div>
            <!-- Col 2 -->
            <div class="footer-col">
                <h4>Noetica Mission</h4>
                <p>Empowering researchers to decode complex biological systems through uncompromised structural truth and open-source intelligence.</p>
                <br>
                <a href="index.html">Learn more about Noetica &rarr;</a>
            </div>
            <!-- Col 3 -->
            <div class="footer-col">
                <h4>Filter Suitability Guide</h4>
                <div class="filter-guide-stack">
                    <span class="filter-tag tag-class-1">Class I — Active / Disordered</span>
                    <span class="filter-tag tag-class-2">Class II — Active / Druggable</span>
                    <span class="filter-tag tag-class-3">Class III — Stale / Druggable</span>
                    <span class="filter-tag tag-class-4">Class IV — Indeterminate</span>
                </div>
            </div>
            <!-- Col 4 -->
            <div class="footer-col">
                <h4>Quick Links</h4>
                <ul class="footer-links-list">
                    <li><a href="index.html">Home</a></li>
                    <li><a href="principles.html">Documentation</a></li>
                    <li><a href="architecture.html">Engine</a></li>
                    <li><a href="#beta-registration">Beta Program</a></li>
                    <li><a href="#">Blog</a></li>
                    <li><a href="#">About</a></li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Bottom Most Footer -->
    <div class="bottom-footer">
        <div>&copy; 2026 Noetica. All rights reserved.</div>
        <div class="bottom-footer-center">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Use</a>
            <a href="#">Contact</a>
        </div>
        <div>Built with <span style="color: #ef4444;">&#10084;</span> for science and humanity.</div>
    </div>
"""

index_core_questions = """
                <h1>The Eight Core Questions</h1>
                <p style="font-size: 1.1rem; color: var(--color-text-secondary); margin-bottom: 2rem;">Every discovery processed by the Noetica Engine must answer the following eight questions.</p>
                
                <div class="core-questions-grid">
                    <!-- Q1 -->
                    <a href="principles.html" class="cq-card" data-color="orange" style="text-decoration:none;">
                        <div class="cq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
                        </div>
                        <div>
                            <span class="cq-number">01</span>
                            <div class="cq-title">Foundational Validity</div>
                            <div class="cq-desc">Does this finding rest on established biomechanical laws?</div>
                        </div>
                    </a>
                    
                    <!-- Q2 -->
                    <a href="architecture.html" class="cq-card" data-color="green" style="text-decoration:none;">
                        <div class="cq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                        </div>
                        <div>
                            <span class="cq-number">02</span>
                            <div class="cq-title">Signal Integrity</div>
                            <div class="cq-desc">Is the data clean, robust, and free from experimental artifact?</div>
                        </div>
                    </a>
                    
                    <!-- Q3 -->
                    <a href="ingestion.html" class="cq-card" data-color="blue" style="text-decoration:none;">
                        <div class="cq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                        </div>
                        <div>
                            <span class="cq-number">03</span>
                            <div class="cq-title">Structural Completeness</div>
                            <div class="cq-desc">Are all relevant molecular interactions mapped comprehensively?</div>
                        </div>
                    </a>

                    <!-- Q4 -->
                    <a href="scoring.html" class="cq-card" data-color="red" style="text-decoration:none;">
                        <div class="cq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                        </div>
                        <div>
                            <span class="cq-number">04</span>
                            <div class="cq-title">Therapeutic Viability</div>
                            <div class="cq-desc">Can this insight be realistically translated into a treatment?</div>
                        </div>
                    </a>
                    
                    <!-- Q5 -->
                    <a href="#" class="cq-card" data-color="purple" style="text-decoration:none;">
                        <div class="cq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M16 12l-4-4-4 4"></path><path d="M12 16V8"></path></svg>
                        </div>
                        <div>
                            <span class="cq-number">05</span>
                            <div class="cq-title">Causal Confidence</div>
                            <div class="cq-desc">Does this demonstrate causality, or merely correlation?</div>
                        </div>
                    </a>

                    <!-- Q6 -->
                    <a href="#" class="cq-card" data-color="teal" style="text-decoration:none;">
                        <div class="cq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                        </div>
                        <div>
                            <span class="cq-number">06</span>
                            <div class="cq-title">Temporal Dynamics</div>
                            <div class="cq-desc">How does this mechanism evolve across time and states?</div>
                        </div>
                    </a>

                    <!-- Q7 -->
                    <a href="#" class="cq-card" data-color="amber" style="text-decoration:none;">
                        <div class="cq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        </div>
                        <div>
                            <span class="cq-number">07</span>
                            <div class="cq-title">Literature Context</div>
                            <div class="cq-desc">Does it align with or refute the current body of open knowledge?</div>
                        </div>
                    </a>

                    <!-- Q8 -->
                    <a href="#" class="cq-card" data-color="blue-alt" style="text-decoration:none;">
                        <div class="cq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                        </div>
                        <div>
                            <span class="cq-number">08</span>
                            <div class="cq-title">Reproducibility</div>
                            <div class="cq-desc">Can this outcome be consistently achieved independently?</div>
                        </div>
                    </a>
                </div>
"""

toc_replacements = {
    '<span class="num">1</span>': '<span class="num">01.</span>',
    '<span class="num">2</span>': '<span class="num">02.</span>',
    '<span class="num">3</span>': '<span class="num">03.</span>',
    '<span class="num">4</span>': '<span class="num">04.</span>',
    '<span class="num">5</span>': '<span class="num">05.</span>'
}

for filename in html_files:
    if not os.path.exists(filename): continue
    with io.open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace old waitlist banner (regex to catch variations)
    content = re.sub(
        r'<div class="beta-cta reveal-on-scroll" id="beta-registration">.*?</div>',
        waitlist_banner,
        content,
        flags=re.DOTALL
    )
    
    # Apply TOC leading zero replacements
    for old, new in toc_replacements.items():
        content = content.replace(old, new)
        
    # Inject Back to Noetica Home button at end of sidebar
    if 'class="sidebar-back-btn"' not in content:
        content = content.replace('</nav>\n    </aside>', sidebar_back_btn + '\n    </nav>\n    </aside>')
        
    # Replace existing footer logic
    content = re.sub(
        r'<footer style="margin-top: 5rem; padding: 2rem 0; text-align: center; border-top: 1px solid var\(--color-border\); color: var\(--color-text-muted\); font-size: 0\.85rem;">.*?</footer>',
        new_footers,
        content,
        flags=re.DOTALL
    )
    
    if filename == 'index.html':
        content = re.sub(
            r'<h1>Noetica Documentation.*?</div>\s*</div>',
            index_core_questions,
            content,
            flags=re.DOTALL
        )
    
    with io.open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated HTML files for waitlist, footer, and sidebar.")

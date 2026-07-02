import os
import re

html_files = [
    'architecture.html', 'index.html', 'ingestion.html', 
    'principles.html', 'scoring.html', 'timelines.html'
]

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
                <a href="https://docs.google.com/forms/d/e/1FAIpQLSeZvfiWcRGqm3fzzJucT3UB6cfgXDRzj42rfrR8yf6dcm9F_w/viewform?usp=dialog" class="btn-waitlist" target="_blank">Join the Waitlist &rarr;</a>
                <small>Opens in Google Form</small>
            </div>
        </div>
"""

core_questions_grid = """
            <section class="doc-section" style="margin-top: 4rem;">
                <h2 class="reveal-on-scroll">The 8 Core Questions</h2>
                <div class="core-questions-grid">
                    <div class="cq-card cq-orange reveal-on-scroll">
                        <div class="cq-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg></div>
                        <h4>Does it solve the problem?</h4>
                        <p>Evaluates functional efficacy against stated objectives.</p>
                    </div>
                    <div class="cq-card cq-green reveal-on-scroll" style="transition-delay: 50ms;">
                        <div class="cq-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg></div>
                        <h4>Is it safe?</h4>
                        <p>Validates biomechanical tolerance and side-effect profiles.</p>
                    </div>
                    <div class="cq-card cq-blue reveal-on-scroll" style="transition-delay: 100ms;">
                        <div class="cq-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg></div>
                        <h4>Is the structure sound?</h4>
                        <p>Analyzes molecular or systemic architectural integrity.</p>
                    </div>
                    <div class="cq-card cq-red reveal-on-scroll" style="transition-delay: 150ms;">
                        <div class="cq-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h4l2-9 5 18 3-10h4"></path></svg></div>
                        <h4>What is the mechanism?</h4>
                        <p>Identifies precise pathways of action, rejecting black-box claims.</p>
                    </div>
                    <div class="cq-card cq-purple reveal-on-scroll" style="transition-delay: 200ms;">
                        <div class="cq-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg></div>
                        <h4>Who proved it?</h4>
                        <p>Weighs evidence source credibility over volume of citations.</p>
                    </div>
                    <div class="cq-card cq-teal reveal-on-scroll" style="transition-delay: 250ms;">
                        <div class="cq-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg></div>
                        <h4>How fast does it act?</h4>
                        <p>Temporal profiling of systemic onset and duration.</p>
                    </div>
                    <div class="cq-card cq-amber reveal-on-scroll" style="transition-delay: 300ms;">
                        <div class="cq-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg></div>
                        <h4>Who benefits most?</h4>
                        <p>Patient/demographic stratification for maximum efficacy.</p>
                    </div>
                    <div class="cq-card cq-blue reveal-on-scroll" style="transition-delay: 350ms;">
                        <div class="cq-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg></div>
                        <h4>Can it scale?</h4>
                        <p>Assesses manufacturability and real-world deployment viability.</p>
                    </div>
                </div>
            </section>
"""

proper_footers = """    <!-- 4-Column Footer -->
    <div class="pre-footer-wrapper">
        <div class="pre-footer-grid">
            <!-- Col 1 -->
            <div class="footer-col">
                <img src="creator.jpg" alt="Sk Anish Md." class="creator-avatar">
                <h4>Sk Anish Md.</h4>
                <p>A Bioinformatics student, developer, and researcher building tools that accelerate scientific discovery through AI, data, and open knowledge.</p>
                <div class="footer-socials">
                    <a href="https://github.com/skanishmd" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg></a>
                    <a href="https://www.linkedin.com/in/skanishmd" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg></a>
                    <a href="mailto:skanishmd321@gmail.com"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg></a>
                    <a href="https://www.instagram.com/sk4nishmd" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg></a>
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
                    <span class="filter-tag tag-class-1">Class I &mdash; Active / Disordered</span>
                    <span class="filter-tag tag-class-2">Class II &mdash; Active / Druggable</span>
                    <span class="filter-tag tag-class-3">Class III &mdash; Stale / Druggable</span>
                    <span class="filter-tag tag-class-4">Class IV &mdash; Indeterminate</span>
                </div>
            </div>
            <!-- Col 4 -->
            <div class="footer-col">
                <h4>Quick Links</h4>
                <ul class="footer-links-list">
                    <li><a href="index.html">Home</a></li>
                    <li><a href="principles.html">Documentation</a></li>
                    <li><a href="architecture.html">Engine</a></li>
                    <li><a href="index.html#beta-registration">Beta Program</a></li>
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

    <script src="app.js"></script>
</body>
</html>
"""

import io
for filename in html_files:
    if not os.path.exists(filename): continue
    with io.open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: Clean everything after </main>
    main_end = content.find('</main>')
    if main_end != -1:
        content = content[:main_end] # keep everything up to just BEFORE </main>
    else:
        print("Warning: no </main> in {}".format(filename))
        continue
    
    # Step 2: For ALL pages, remove the old Waitlist / Beta Section if it exists inside <main>
    # (Because we will append it cleanly at the end of <main>)
    # Find <!-- Waitlist / Beta Section --> and remove it to the end of content
    waitlist_idx = content.find('<!-- Waitlist / Beta Section -->')
    if waitlist_idx != -1:
        content = content[:waitlist_idx]
    
    # Step 3: For index.html, inject the Core Questions grid right before waitlist if not present
    if filename == 'index.html':
        if '8 Core Questions' not in content:
            # We want to insert the core questions into the reading-pane.
            # In index.html, the reading-pane closes with '</div>'. Let's find the LAST '</div>' in content
            # wait, reading-pane is closed. Let's just append it. BUT it must be inside <div class="reading-pane">!
            reading_pane_close = content.rfind('</div>')
            if reading_pane_close != -1:
                content = content[:reading_pane_close] + core_questions_grid + content[reading_pane_close:]
    
    # Step 4: Add the waitlist banner and close </main>
    content += waitlist_banner
    content += '    </main>\n\n'
    
    # Step 5: Add proper footers and body closing
    content += proper_footers
    
    # Replace â†’ with &rarr; just in case any leaked through
    content = content.replace(u'\xe2\x86\x92', u'&rarr;')

    with io.open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

# Update index.css to ensure core questions and waitlist styling is perfectly intact
css_append = """
/* Core Questions Grid */
.core-questions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.cq-card {
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease, background 0.3s ease;
}

.cq-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.02);
}
[data-theme='light'] .cq-card:hover {
    background: rgba(0, 0, 0, 0.02);
}

.cq-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    color: white;
}

.cq-card h4 {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--color-text-primary);
}

.cq-card p {
    font-size: 0.9rem;
    color: var(--color-text-muted);
    line-height: 1.5;
    margin: 0;
}

/* Color Themes for Cards */
.cq-orange .cq-icon { background: linear-gradient(135deg, #f97316, #ea580c); }
.cq-orange:hover { border-color: rgba(249, 115, 22, 0.4); box-shadow: 0 10px 30px rgba(249, 115, 22, 0.1); }

.cq-green .cq-icon { background: linear-gradient(135deg, #10b981, #059669); }
.cq-green:hover { border-color: rgba(16, 185, 129, 0.4); box-shadow: 0 10px 30px rgba(16, 185, 129, 0.1); }

.cq-blue .cq-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.cq-blue:hover { border-color: rgba(59, 130, 246, 0.4); box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1); }

.cq-red .cq-icon { background: linear-gradient(135deg, #ef4444, #dc2626); }
.cq-red:hover { border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 10px 30px rgba(239, 68, 68, 0.1); }

.cq-purple .cq-icon { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.cq-purple:hover { border-color: rgba(139, 92, 246, 0.4); box-shadow: 0 10px 30px rgba(139, 92, 246, 0.1); }

.cq-teal .cq-icon { background: linear-gradient(135deg, #14b8a6, #0d9488); }
.cq-teal:hover { border-color: rgba(20, 184, 166, 0.4); box-shadow: 0 10px 30px rgba(20, 184, 166, 0.1); }

.cq-amber .cq-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }
.cq-amber:hover { border-color: rgba(245, 158, 11, 0.4); box-shadow: 0 10px 30px rgba(245, 158, 11, 0.1); }

"""

with io.open('index.css', 'r', encoding='utf-8') as f:
    css = f.read()

if '.core-questions-grid' not in css:
    with io.open('index.css', 'a', encoding='utf-8') as f:
        f.write(css_append)

print("HTML cleanup complete.")

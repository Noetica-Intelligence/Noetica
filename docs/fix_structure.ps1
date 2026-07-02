$html_files = @('architecture.html', 'index.html', 'ingestion.html', 'principles.html', 'scoring.html', 'timelines.html')

$waitlist_banner = @"
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
"@

$core_questions_grid = @"
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
"@

$proper_footers = @"
    <!-- 4-Column Footer -->
    <div class="pre-footer-wrapper">
        <div class="pre-footer-grid">
            <!-- Col 1 -->
            <div class="footer-col">
                <img src="creator.jpg" alt="Sk Anish Md." class="creator-avatar" style="width: 60px; height: 60px; object-fit: cover; border: 2px solid var(--color-border);">
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
"@

foreach ($file in $html_files) {
    if (Test-Path $file) {
        $content = Get-Content -Path $file -Raw
        
        # Clean everything after </main>
        $mainIdx = $content.IndexOf("</main>")
        if ($mainIdx -ge 0) {
            $content = $content.Substring(0, $mainIdx)
        }
        
        # Remove waitlist banner if it somehow exists before </main>
        $waitlistIdx = $content.IndexOf("<!-- Waitlist / Beta Section -->")
        if ($waitlistIdx -ge 0) {
            $content = $content.Substring(0, $waitlistIdx)
        }
        
        # For index.html, inject core questions
        if ($file -eq 'index.html' -and $content.IndexOf("8 Core Questions") -eq -1) {
            $readingPaneClose = $content.LastIndexOf("</div>")
            if ($readingPaneClose -ge 0) {
                $content = $content.Insert($readingPaneClose, $core_questions_grid)
            }
        }
        
        # Append clean ending
        $content = $content + $waitlist_banner + "    </main>`r`n`r`n"
        $content = $content + $proper_footers
        
        # Ensure arrows are proper HTML entities, not corrupted ANSI characters
        $content = $content.Replace("â†’", "&rarr;")
        
        Set-Content -Path $file -Value $content -Encoding UTF8
    }
}
Write-Output "Fixed HTML structures successfully!"

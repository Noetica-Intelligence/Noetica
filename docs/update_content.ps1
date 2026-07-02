$html_files = @('architecture.html', 'index.html', 'ingestion.html', 'principles.html', 'scoring.html', 'timelines.html')

foreach ($file in $html_files) {
    if (Test-Path $file) {
        $content = Get-Content -Path $file -Raw
        
        # 1. Remove "The 8 Core Questions"
        $content = $content -replace '(?s)<section class="doc-section"[^>]*>\s*<h2[^>]*>The 8 Core Questions</h2>.*?</section>', ''
        
        # 2. Remove "Product Preview Image"
        $content = $content -replace '(?s)<div class="product-preview[^>]*>.*?</div>\s*<h2', '<h2'
        
        # 3. Remove "Filter Suitability Guide" (Col 3)
        $content = $content -replace '(?s)<!-- Col 3 -->\s*<div class="footer-col">\s*<h4>Filter Suitability Guide</h4>.*?</div>\s*<!-- Col 4 -->', '<!-- Col 4 -->'
        
        # 4. Update Footer Socials to have colors
        $socials_old = '(?s)<div class="footer-socials">\s*<a href="https://github.com/skanishmd"[^>]*>(.*?)</a>\s*<a href="https://www.linkedin.com/in/skanishmd"[^>]*>(.*?)</a>\s*<a href="mailto:skanishmd321@gmail.com"[^>]*>(.*?)</a>\s*<a href="https://www.instagram.com/sk4nishmd"[^>]*>(.*?)</a>\s*</div>'
        
        $socials_new = '<div class="footer-socials">
                    <a href="https://github.com/skanishmd" target="_blank" style="color: #ef4444; border-color: rgba(239, 68, 68, 0.4);" onmouseover="this.style.background=''#ef4444''; this.style.color=''white''" onmouseout="this.style.background=''''; this.style.color=''#ef4444''">$1</a>
                    <a href="https://www.linkedin.com/in/skanishmd" target="_blank" style="color: #3b82f6; border-color: rgba(59, 130, 246, 0.4);" onmouseover="this.style.background=''#3b82f6''; this.style.color=''white''" onmouseout="this.style.background=''''; this.style.color=''#3b82f6''">$2</a>
                    <a href="mailto:skanishmd321@gmail.com" style="color: #f59e0b; border-color: rgba(245, 158, 11, 0.4);" onmouseover="this.style.background=''#f59e0b''; this.style.color=''white''" onmouseout="this.style.background=''''; this.style.color=''#f59e0b''">$3</a>
                    <a href="https://www.instagram.com/sk4nishmd" target="_blank" style="color: #10b981; border-color: rgba(16, 185, 129, 0.4);" onmouseover="this.style.background=''#10b981''; this.style.color=''white''" onmouseout="this.style.background=''''; this.style.color=''#10b981''">$4</a>
                </div>'
        $content = $content -replace $socials_old, $socials_new
        
        # 5. Fix corrupted chars manually by identifying the byte pattern
        $content = $content -replace 'â€”', '&mdash;'
        $content = $content -replace 'â€', '&mdash;'
        
        Set-Content -Path $file -Value $content -Encoding UTF8
    }
}

# 6. Make Waitlist Banner more compact and aesthetic in CSS
$css_content = Get-Content -Path "index.css" -Raw
$css_old = '(?s)\.waitlist-banner \{.*?\}'
$css_new = '.waitlist-banner {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.5), rgba(59, 130, 246, 0.08));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1rem 1.5rem;
    margin: 3rem 0 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}'
$css_content = $css_content -replace $css_old, $css_new

$waitlist_h3_old = '(?s)\.waitlist-content h3 \{.*?\}'
$waitlist_h3_new = '.waitlist-content h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem; }'
$css_content = $css_content -replace $waitlist_h3_old, $waitlist_h3_new

$waitlist_p_old = '(?s)\.waitlist-content p \{.*?\}'
$waitlist_p_new = '.waitlist-content p { color: var(--color-text-muted); font-size: 0.85rem; margin-bottom: 0.5rem; }'
$css_content = $css_content -replace $waitlist_p_old, $waitlist_p_new

$waitlist_action_old = '(?s)\.waitlist-action \{.*?\}'
$waitlist_action_new = '.waitlist-action { display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem; flex-shrink: 0; }'
$css_content = $css_content -replace $waitlist_action_old, $waitlist_action_new

$waitlist_btn_old = '(?s)\.btn-waitlist \{.*?\}'
$waitlist_btn_new = '.btn-waitlist {
    position: relative;
    display: inline-block;
    background: linear-gradient(90deg, #3b82f6, #6366f1);
    color: white !important;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 0.6rem 1.25rem;
    border-radius: 8px;
    text-decoration: none;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}'
$css_content = $css_content -replace $waitlist_btn_old, $waitlist_btn_new

# Also fix the footer socials in CSS to NOT override the inline colors on hover globally
$socials_css_old = '(?s)\.footer-socials a:hover \{.*?\}'
$socials_css_new = '.footer-socials a:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}'
$css_content = $css_content -replace $socials_css_old, $socials_css_new

Set-Content -Path "index.css" -Value $css_content -Encoding UTF8

Write-Output "Content updated successfully."

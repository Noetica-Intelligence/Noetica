document.addEventListener('DOMContentLoaded', () => {
    // --- THEME TOGGLE LOGIC ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const iconSun = document.getElementById('theme-icon-sun');
    const iconMoon = document.getElementById('theme-icon-moon');
    const iconSystem = document.getElementById('theme-icon-system');
    const themeText = document.getElementById('theme-text');
    
    // States: 'system', 'light', 'dark'
    const THEMES = ['system', 'light', 'dark'];
    
    function updateThemeUI(theme) {
        // Hide all icons
        iconSun.style.display = 'none';
        iconMoon.style.display = 'none';
        iconSystem.style.display = 'none';
        
        if (theme === 'light') {
            iconSun.style.display = 'block';
            themeText.innerText = 'Light';
        } else if (theme === 'dark') {
            iconMoon.style.display = 'block';
            themeText.innerText = 'Dark';
        } else {
            iconSystem.style.display = 'block';
            themeText.innerText = 'System';
        }
    }
    
    function applyTheme(theme) {
        if (theme === 'system') {
            const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-theme', systemDark ? 'dark' : 'light');
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }
        updateThemeUI(theme);
    }
    
    // Initialize
    let currentTheme = localStorage.getItem('theme') || 'system';
    applyTheme(currentTheme);
    
    // Cycle theme on click
    themeToggleBtn.addEventListener('click', () => {
        let currentIndex = THEMES.indexOf(currentTheme);
        currentIndex = (currentIndex + 1) % THEMES.length;
        currentTheme = THEMES[currentIndex];
        localStorage.setItem('theme', currentTheme);
        applyTheme(currentTheme);
    });
    
    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (currentTheme === 'system') {
            applyTheme('system');
        }
    });

    // --- SCROLL PROGRESS BAR LOGIC ---
    const scrollProgress = document.getElementById('scroll-progress');
    
    function updateScrollProgress() {
        if (!scrollProgress) return;
        const scrollPx = document.documentElement.scrollTop || document.body.scrollTop;
        const winHeightPx = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = winHeightPx > 0 ? (scrollPx / winHeightPx) * 100 : 0;
        scrollProgress.style.width = scrolled + '%';
    }

    // Use requestAnimationFrame for smooth 60fps performance without thrashing
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                updateScrollProgress();
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });
    
    // Initial call in case the page is already scrolled on load
    updateScrollProgress();

    // --- INTERSECTION OBSERVER FOR SCROLL REVEALS ---
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    
    // Respect prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (!prefersReducedMotion && 'IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Stagger effect if multiple elements appear at once
                    setTimeout(() => {
                        entry.target.classList.add('is-visible');
                    }, index * 50); // 50ms stagger
                    observer.unobserve(entry.target); // Only animate once
                }
            });
        }, {
            root: null,
            rootMargin: '0px 0px -50px 0px', // Trigger slightly before the element fully enters
            threshold: 0.1
        });

        revealElements.forEach(el => revealObserver.observe(el));
    } else {
        // Fallback if reduced motion is enabled or IntersectionObserver is missing
        revealElements.forEach(el => el.classList.add('is-visible'));
    }
});

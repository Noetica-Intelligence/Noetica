document.addEventListener('DOMContentLoaded', () => {
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
});

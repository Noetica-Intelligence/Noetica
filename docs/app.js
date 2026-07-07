document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("dashboard_data.json");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        const paradigmList = document.getElementById("paradigm-list");
        const discoveryGrid = document.getElementById("discovery-grid");
        const currentParadigmTitle = document.getElementById("current-paradigm");
        
        let currentParadigm = data.paradigms[0]; // Default to first

        // Render Sidebar
        data.paradigms.forEach(paradigm => {
            const li = document.createElement("li");
            li.className = "paradigm-item";
            if (paradigm === currentParadigm) li.classList.add("active");
            li.textContent = paradigm;
            
            li.addEventListener("click", () => {
                document.querySelectorAll(".paradigm-item").forEach(el => el.classList.remove("active"));
                li.classList.add("active");
                currentParadigm = paradigm;
                renderGrid();
            });
            
            paradigmList.appendChild(li);
        });

        // Render Grid
        function renderGrid() {
            currentParadigmTitle.textContent = currentParadigm;
            discoveryGrid.innerHTML = ""; // Clear existing
            
            // Animation staggered delay
            let delay = 0;

            data.types.forEach(type => {
                const item = data.matrix[currentParadigm][type];
                if (!item) return;

                const card = document.createElement("div");
                card.className = "card";
                card.style.animation = `fadeInUp 0.5s ease forwards ${delay}s`;
                card.style.opacity = "0"; // Initial state for animation

                card.innerHTML = `
                    <div class="card-type">${type}</div>
                    <div class="card-score">NET: ${item.score.toFixed(1)}</div>
                    <h3 class="card-title">${item.title}</h3>
                    <div class="card-authors">${item.authors}</div>
                    <div class="card-abstract">${item.abstract}</div>
                    <a href="${item.url}" class="card-link" target="_blank">Explore Discovery →</a>
                `;
                
                discoveryGrid.appendChild(card);
                delay += 0.08;
            });
        }
        
        // Initial render
        renderGrid();

    } catch (err) {
        console.error("Failed to load dashboard data:", err);
        document.getElementById("current-paradigm").textContent = "Error loading data.";
    }
});

// Add animation styles dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

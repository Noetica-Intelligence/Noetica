document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("dashboard_data.json");
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        
        const paradigmList = document.getElementById("paradigm-list");
        const discoveryGrid = document.getElementById("discovery-grid");
        const currentParadigmTitle = document.getElementById("current-paradigm");
        
        let currentParadigm = data.paradigms[0];

        // ── Render Sidebar ──
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

        // ── Helper: Score color ──
        function scoreColor(score) {
            if (score >= 8.5) return { bg: "rgba(16,185,129,0.15)", fg: "#10b981", border: "rgba(16,185,129,0.3)" };
            if (score >= 7.0) return { bg: "rgba(56,189,248,0.15)", fg: "#38bdf8", border: "rgba(56,189,248,0.3)" };
            if (score >= 5.0) return { bg: "rgba(251,191,36,0.15)", fg: "#fbbf24", border: "rgba(251,191,36,0.3)" };
            return { bg: "rgba(148,163,184,0.15)", fg: "#94a3b8", border: "rgba(148,163,184,0.3)" };
        }

        // ── Helper: Status badge color ──
        function statusColor(status) {
            if (status === "Breakthrough Signal") return "#10b981";
            if (status === "Strong Signal") return "#38bdf8";
            return "#94a3b8";
        }

        // ── Helper: NET sub-score bar ──
        function subScoreBar(label, value) {
            const pct = Math.min(value / 10 * 100, 100);
            const clr = scoreColor(value);
            return `
                <div class="subscore-row">
                    <span class="subscore-label">${label}</span>
                    <div class="subscore-track">
                        <div class="subscore-fill" style="width:${pct}%;background:${clr.fg};"></div>
                    </div>
                    <span class="subscore-value" style="color:${clr.fg};">${value.toFixed(1)}</span>
                </div>
            `;
        }

        // ── Render Grid ──
        function renderGrid() {
            currentParadigmTitle.textContent = currentParadigm;
            discoveryGrid.innerHTML = "";
            
            let delay = 0;

            data.types.forEach(type => {
                const item = data.matrix[currentParadigm][type];
                if (!item) return;

                const card = document.createElement("div");
                card.className = "card";
                card.style.animation = `fadeInUp 0.5s ease forwards ${delay}s`;
                card.style.opacity = "0";

                const sc = scoreColor(item.score);
                const stColor = statusColor(item.status);

                // Build action buttons
                let sourceBtn = "";
                if (item.url && item.url !== "#") {
                    sourceBtn = `<a href="${item.url}" class="btn-source" target="_blank" rel="noopener">View Source</a>`;
                }

                let pdfBtn = "";
                if (item.pdf_url) {
                    pdfBtn = `<a href="${item.pdf_url}" class="btn-pdf" target="_blank" rel="noopener">Open PDF</a>`;
                }

                // Knowledge graph edge
                let kgHtml = "";
                if (item.knowledge_graph_edge) {
                    kgHtml = `
                        <div class="kg-section">
                            <div class="kg-label">Knowledge Graph Vector</div>
                            <div class="kg-box">⮑ ${item.knowledge_graph_edge}</div>
                        </div>
                    `;
                }

                // Strategic implication
                let stratHtml = "";
                if (item.strategic_implication) {
                    stratHtml = `
                        <div class="strat-section">
                            <div class="strat-label">Strategic Implication</div>
                            <div class="strat-text">${item.strategic_implication}</div>
                        </div>
                    `;
                }

                card.innerHTML = `
                    <div class="card-header-row">
                        <div class="card-type">${type}</div>
                        <div class="card-score" style="background:${sc.bg};color:${sc.fg};border-color:${sc.border};">
                            NET: ${item.score.toFixed(1)}/10
                        </div>
                    </div>

                    <div class="card-status" style="color:${stColor};">● ${item.status || "Emerging Signal"}</div>
                    
                    <h3 class="card-title">${item.title}</h3>
                    
                    <div class="card-meta">
                        <span class="card-authors">${item.authors}</span>
                        ${item.source ? `<span class="card-source">↳ Source: ${item.source_agg || item.source}</span>` : ""}
                    </div>
                    
                    <div class="card-abstract">${item.abstract}</div>

                    ${stratHtml}
                    ${kgHtml}

                    <div class="net-breakdown">
                        <div class="net-breakdown-title">NET Framework Breakdown</div>
                        ${subScoreBar("Novelty", item.novelty || 0)}
                        ${subScoreBar("Evidence", item.evidence || 0)}
                        ${subScoreBar("Trend", item.trend || 0)}
                    </div>

                    <div class="card-actions">
                        ${sourceBtn}
                        ${pdfBtn}
                    </div>

                    <div class="card-calibrate">
                        <span class="calibrate-label">Calibrate Model:</span>
                        <button class="btn-useful" onclick="calibrate('${item.title}', 'useful')">👍 Useful</button>
                        <button class="btn-noise" onclick="calibrate('${item.title}', 'noise')">👎 Noise</button>
                    </div>
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

// ── Calibrate Model (Feedback) ──
function calibrate(title, type) {
    const btn = event.target;
    btn.classList.add("calibrated");
    
    // Store feedback in localStorage
    const feedbackKey = `noetica_feedback_${btoa(title).substring(0, 20)}`;
    localStorage.setItem(feedbackKey, type);
    
    // Visual feedback
    if (type === "useful") {
        btn.textContent = "✓ Logged";
        btn.style.background = "rgba(16,185,129,0.3)";
        btn.style.color = "#10b981";
    } else {
        btn.textContent = "✓ Logged";
        btn.style.background = "rgba(239,68,68,0.3)";
        btn.style.color = "#ef4444";
    }
    btn.disabled = true;
}

// ── Animation Keyframes ──
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

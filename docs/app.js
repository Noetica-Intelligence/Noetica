// Determine if we are running locally or on GitHub Pages
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = isLocal 
    ? 'http://localhost:8001/api/v1' 
    : 'https://noetica-engine.onrender.com/api/v1';

// 1. Fetch and render Discoveries in Sidebar
async function loadDiscoveries() {
    try {
        const res = await fetch(`${API_BASE}/discoveries/`);
        const discoveries = await res.json();
        
        const listEl = document.getElementById('discovery-list');
        listEl.innerHTML = '';

        discoveries.forEach(d => {
            const card = document.createElement('div');
            card.className = 'discovery-card';
            // Attach click handler to open the modal
            card.onclick = () => openModal(d.id);
            card.innerHTML = `
                <h3 class="d-title">${d.title}</h3>
                <div class="d-meta">
                    <span class="d-domain">${d.domain}</span>
                    <span class="d-score">Impact: ${(d.score * 100).toFixed(1)}</span>
                </div>
            `;
            listEl.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load discoveries", err);
    }
}

// Modal Logic
async function openModal(discoveryId) {
    const modal = document.getElementById('discovery-modal');
    const titleEl = document.getElementById('modal-title');
    const tagsEl = document.getElementById('modal-tags');
    const abstractEl = document.getElementById('modal-abstract');
    const sourcesEl = document.getElementById('modal-sources');

    // Reset contents
    titleEl.innerText = "Processing Data...";
    tagsEl.innerHTML = "";
    abstractEl.innerHTML = "";
    sourcesEl.innerHTML = "";
    
    modal.classList.add('active');

    try {
        const res = await fetch(`${API_BASE}/discoveries/${discoveryId}`);
        if (!res.ok) throw new Error("API returned " + res.status);
        const d = await res.json();

        titleEl.innerText = d.title;
        
        tagsEl.innerHTML = `
            <span class="modal-tag domain">${d.domain}</span>
            <span class="modal-tag status">Status: ${d.status}</span>
            <span class="modal-tag impact">Impact: ${(d.score * 100).toFixed(1)}</span>
        `;

        abstractEl.innerText = d.abstract || "No abstract available for this discovery.";

        if (d.sources && d.sources.length > 0) {
            sourcesEl.innerHTML = d.sources.map(s => 
                `<a href="${s}" target="_blank">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    Source Link
                </a>`
            ).join('');
        }
    } catch (err) {
        console.error(err);
        titleEl.innerText = "Error loading discovery details";
    }
}

function closeModal() {
    document.getElementById('discovery-modal').classList.remove('active');
}

// Close modal when clicking outside of it
document.getElementById('discovery-modal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// 2. Fetch and render 3D Knowledge Graph
async function loadGraph() {
    try {
        const res = await fetch(`${API_BASE}/knowledge-graph/`);
        const graphData = await res.json();

        document.getElementById('loader').style.display = 'none';

        // Vibrant neon color palette matching the new CSS
        const colors = {
            technology: '#00f0ff', // Cyan
            concept: '#ec4899',    // Pink
            default: '#a855f7',    // Purple
            bg: '#04070a',         // Deep Space Background
            links: 'rgba(0, 240, 255, 0.15)'
        };

        const Graph = window.Graph = ForceGraph3D()
            (document.getElementById('3d-graph'))
            .graphData(graphData)
            .nodeLabel('name')
            .nodeColor(node => node.group === 'Technology' ? colors.technology : (node.group === 'Concept' ? colors.concept : colors.default))
            .nodeRelSize(6)
            .linkWidth(1.5)
            .linkColor(() => colors.links)
            .linkDirectionalParticles(4) // More particles
            .linkDirectionalParticleWidth(3.5) // Thicker laser beams
            .linkDirectionalParticleColor(link => {
                // Randomly assign cyan or purple laser beams to links for a dynamic look
                return Math.random() > 0.5 ? colors.technology : colors.default;
            })
            .linkDirectionalParticleSpeed(d => d.value * 0.005 || 0.006)
            .backgroundColor(colors.bg)
            .onNodeClick(node => {
                // Focus on node
                const distance = 50;
                const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
                
                Graph.cameraPosition(
                    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
                    node, // lookAt
                    2500  // ms transition
                );
            });

        // Add gentle rotation
        let angle = 0;
        setInterval(() => {
            Graph.cameraPosition({
                x: 350 * Math.sin(angle),
                z: 350 * Math.cos(angle)
            });
            angle += Math.PI / 1200;
        }, 30);

    } catch (err) {
        console.error("Failed to load graph", err);
        document.getElementById('loader').innerText = "ERROR LOADING ZIG KNOWLEDGE ENGINE";
        document.getElementById('loader').style.color = "#ec4899";
    }
}

// Initialize
loadDiscoveries();
loadGraph();

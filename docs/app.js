// Determine if we are running locally or on GitHub Pages
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = isLocal 
    ? 'http://localhost:8001/api/v1' 
    : 'https://sk4nishmd-noetica-backend.hf.space/api/v1';

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
                    <span class="d-score">Score: ${(d.score * 100).toFixed(1)}</span>
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
    titleEl.innerText = "Loading data...";
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
            <span class="modal-tag">${d.domain}</span>
            <span class="modal-tag">Status: ${d.status}</span>
            <span class="modal-tag">Impact: ${(d.score * 100).toFixed(1)}</span>
        `;

        abstractEl.innerText = d.abstract || "No abstract available for this discovery.";

        if (d.sources && d.sources.length > 0) {
            sourcesEl.innerHTML = d.sources.map(s => 
                `<a href="${s}" target="_blank">📄 Source Link</a>`
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

        const Graph = window.Graph = ForceGraph3D()
            (document.getElementById('3d-graph'))
            .graphData(graphData)
            .nodeLabel('name')
            .nodeColor(node => node.group === 'Technology' ? '#66fcf1' : (node.group === 'Concept' ? '#ff0055' : '#8a2be2'))
            .nodeRelSize(6)
            .linkWidth(1.5)
            .linkColor(() => 'rgba(102, 252, 241, 0.2)')
            .linkDirectionalParticles(3) // Adds the moving laser beams
            .linkDirectionalParticleWidth(2.5)
            .linkDirectionalParticleColor(() => '#ffffff')
            .linkDirectionalParticleSpeed(d => d.value * 0.005 || 0.005)
            .backgroundColor('#020205') // Deeper pitch black space
            .onNodeClick(node => {
                // Focus on node
                const distance = 40;
                const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
                
                Graph.cameraPosition(
                    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
                    node, // lookAt
                    3000  // ms transition
                );
            });

        // Add gentle rotation
        let angle = 0;
        setInterval(() => {
            Graph.cameraPosition({
                x: 300 * Math.sin(angle),
                z: 300 * Math.cos(angle)
            });
            angle += Math.PI / 1000;
        }, 30);

    } catch (err) {
        console.error("Failed to load graph", err);
        document.getElementById('loader').innerText = "ERROR LOADING KNOWLEDGE GRAPH";
        document.getElementById('loader').style.color = "#ff4444";
    }
}

// Initialize
loadDiscoveries();
loadGraph();

// Theme Toggle Logic
const themeToggle = document.getElementById('theme-toggle');
const sunIcon = document.getElementById('sun-icon');
const moonIcon = document.getElementById('moon-icon');

// Check for saved theme
const savedTheme = localStorage.getItem('theme') || 'dark';
if (savedTheme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    sunIcon.style.display = 'none';
    moonIcon.style.display = 'block';
}

function updateGraphColors(theme) {
    if (!window.Graph) return;
    
    if (theme === 'light') {
        window.Graph
            .backgroundColor('#f8fafc')
            .nodeColor(node => node.group === 'Technology' ? '#2563eb' : (node.group === 'Concept' ? '#e11d48' : '#7c3aed'))
            .linkColor(() => 'rgba(37, 99, 235, 0.2)')
            .linkDirectionalParticleColor(() => '#1e40af');
    } else {
        window.Graph
            .backgroundColor('#020205')
            .nodeColor(node => node.group === 'Technology' ? '#66fcf1' : (node.group === 'Concept' ? '#ff0055' : '#8a2be2'))
            .linkColor(() => 'rgba(102, 252, 241, 0.2)')
            .linkDirectionalParticleColor(() => '#ffffff');
    }
}

themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    if (newTheme === 'light') {
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
    } else {
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
    }
    
    updateGraphColors(newTheme);
});

// Watch for graph load to apply initial theme colors
const checkGraphInterval = setInterval(() => {
    if (window.Graph) {
        updateGraphColors(document.documentElement.getAttribute('data-theme') || 'dark');
        clearInterval(checkGraphInterval);
    }
}, 100);

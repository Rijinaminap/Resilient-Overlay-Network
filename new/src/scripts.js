const canvas = document.getElementById('network');
const ctx = canvas.getContext('2d');
let networkData = { nodes: [], edges: [], metrics: {} };
let positions = {};

// Fetch the network data from the backend periodically
async function fetchNetwork() {
    try {
        const response = await fetch('http://127.0.0.1:5000/get_network');
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        networkData = await response.json();
        updateMetrics();
        calculatePositions();
        drawNetwork();
    } catch (error) {
        console.error('Error fetching network data:', error);
    }
}

// Update network metrics in the UI
function updateMetrics() {
    const metrics = networkData.metrics || {};
    const packetLoss = metrics.packet_loss || 0;
    const jitter = metrics.jitter || 0;

    document.getElementById('packet-loss').innerText = `Packet Loss: ${packetLoss.toFixed(2)}%`;
    document.getElementById('jitter').innerText = `Jitter: ${jitter.toFixed(2)} ms`;
}

// Calculate positions for nodes
function calculatePositions() {
    const { nodes } = networkData;
    const radius = 200;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    nodes.forEach((node, index) => {
        const angle = (2 * Math.PI * index) / nodes.length;
        positions[node.id] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
        };
    });
}

// Draw the network
function drawNetwork() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const { nodes, edges } = networkData;

    // Draw edges
    edges.forEach(edge => {
        const source = positions[edge.source];
        const target = positions[edge.target];
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle = 'black';
        ctx.stroke();
    });

    // Draw nodes
    nodes.forEach(node => {
        const pos = positions[node.id];
        ctx.fillStyle = 'green'; // Active nodes only
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Label nodes
        ctx.fillStyle = 'black';
        ctx.fillText(node.id, pos.x - 5, pos.y - 15);
    });
}

// Handle node failure
async function failNode() {
    const node = document.getElementById('fail-node').value;
    try {
        const response = await fetch('http://127.0.0.1:5000/fail_node', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ node: parseInt(node) })
        });
        const result = await response.json();
        alert(result.message);
        fetchNetwork(); // Refresh the visualization
    } catch (error) {
        console.error('Error failing node:', error);
    }
}

// Find path between two nodes
async function findPath() {
    const source = document.getElementById('source').value;
    const target = document.getElementById('target').value;
    try {
        const response = await fetch('http://127.0.0.1:5000/reroute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source: parseInt(source), target: parseInt(target) })
        });
        const result = await response.json();

        if (result.status === 'success') {
            alert(`Path: ${result.path.join(' -> ')}`);
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error finding path:', error);
    }
}

fetchNetwork();
setInterval(fetchNetwork, 5000); // Refresh network data every 5 seconds

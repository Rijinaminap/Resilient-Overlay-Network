from flask import Flask, jsonify, request
import networkx as nx
from flask_cors import CORS
import random
import os
import asyncio

app = Flask(__name__)
CORS(app)

# Create a sample network topology
network = nx.Graph()
network.add_edges_from([
    # Layer 1
    (1, 2, {'weight': 1, 'latency': 10}),
    (1, 3, {'weight': 2, 'latency': 15}),
    (1, 4, {'weight': 3, 'latency': 20}),

    # Layer 2
    (2, 5, {'weight': 2, 'latency': 12}),
    (2, 6, {'weight': 1, 'latency': 8}),
    (3, 7, {'weight': 2, 'latency': 10}),
    (3, 8, {'weight': 3, 'latency': 25}),
    (4, 9, {'weight': 4, 'latency': 30}),
    (4, 10, {'weight': 2, 'latency': 15}),

    # Layer 3
    (5, 11, {'weight': 3, 'latency': 18}),
    (6, 12, {'weight': 2, 'latency': 20}),
    (7, 13, {'weight': 1, 'latency': 5}),
    (8, 14, {'weight': 4, 'latency': 22}),
    (9, 15, {'weight': 3, 'latency': 25}),
    (10, 16, {'weight': 2, 'latency': 15}),

    # Interconnections
    (5, 7, {'weight': 3, 'latency': 15}),
    (6, 8, {'weight': 1, 'latency': 10}),
    (9, 11, {'weight': 2, 'latency': 12}),
    (10, 12, {'weight': 3, 'latency': 20}),
    (13, 15, {'weight': 2, 'latency': 10}),
    (14, 16, {'weight': 1, 'latency': 8}),

    # Redundant connections
    (11, 13, {'weight': 3, 'latency': 18}),
    (12, 14, {'weight': 2, 'latency': 12}),
    (15, 16, {'weight': 4, 'latency': 25}),
    (3, 9, {'weight': 2, 'latency': 10}),
    (7, 10, {'weight': 3, 'latency': 15})
])

node_status = {node: True for node in network.nodes}
edge_status = {edge: True for edge in network.edges}

# ------------- FILE HANDLING -------------
def get_file_size(file_path):
    """Get the size of the file in KB."""
    return os.path.getsize(file_path) / 1024  # Size in KB

def read_file(file_path, chunk_size_kb=100):
    """Simulate packet transmission by reading file in chunks."""
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size_kb * 1024):  # Read chunk in bytes
            yield chunk

# ------------- NETWORK ROUTING -------------
def reroute(G, source, target):
    """Find the shortest path from source to target."""
    try:
        path = nx.shortest_path(G, source=source, target=target, weight='weight')
        return path
    except nx.NetworkXNoPath:
        return None

# ------------- FAILURE SIMULATION -------------
def simulate_failure(G, failed_nodes):
    """Simulate node failure by removing nodes."""
    for node in failed_nodes:
        if node in G:
            G.remove_node(node)

@app.route('/get_network', methods=['GET'])
def get_network():
    active_nodes = [node for node, status in node_status.items() if status]
    active_edges = [
        {'source': u, 'target': v, 'weight': data['weight'], 'latency': data['latency']}
        for u, v, data in network.edges(data=True)
        if u in active_nodes and v in active_nodes
    ]
    
    return jsonify({
        "nodes": [{"id": node} for node in active_nodes],
        "edges": active_edges,
        "metrics": {
            "packet_loss": random.uniform(0, 5),
            "jitter": random.uniform(0, 10),
        }
    })

@app.route('/fail_node', methods=['POST'])
def fail_node():
    node = request.json.get('node')
    if node in node_status:
        node_status[node] = False
        return jsonify({"status": "success", "message": f"Node {node} failed"})
    return jsonify({"status": "error", "message": "Invalid node"})

@app.route('/reroute', methods=['POST'])
def reroute_request():
    source = request.json.get('source')
    target = request.json.get('target')

    # Remove failed nodes and edges
    active_network = network.copy()
    for node, status in node_status.items():
        if not status:
            active_network.remove_node(node)

    for edge, status in edge_status.items():
        if not status:
            active_network.remove_edge(*edge)

    path = reroute(active_network, source, target)
    if path:
        return jsonify({"status": "success", "path": path})
    return jsonify({"status": "error", "message": "No path available"})

@app.route('/transmit_file', methods=['POST'])
async def transmit_file():
    source = request.json.get('source')
    target = request.json.get('target')
    file_path = request.json.get('file_path')
    failed_nodes = request.json.get('failed_nodes', [])

    # Simulate network failure
    simulate_failure(network, failed_nodes)

    # Perform transmission
    total_data_transferred = 0
    total_chunks = 0

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File not found"})

    file_size_kb = get_file_size(file_path)
    for chunk in read_file(file_path):
        total_chunks += 1
        chunk_size_kb = len(chunk) / 1024
        total_data_transferred += chunk_size_kb

        path = reroute(network, source, target)
        if path:
            # Simulate transmission of data chunk
            await asyncio.sleep(1)
        else:
            break

    return jsonify({
        "status": "success",
        "total_data_transferred": total_data_transferred,
        "total_chunks": total_chunks
    })

if __name__ == '__main__':
    app.run(debug=True)

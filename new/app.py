from flask import Flask, jsonify, request
import networkx as nx
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

# Create a sample network topology
network = nx.Graph()
network.add_edges_from([
    (1, 2, {'weight': 1, 'latency': 10}),
    (2, 3, {'weight': 2, 'latency': 20}),
    (3, 4, {'weight': 1, 'latency': 5}),
    (1, 4, {'weight': 3, 'latency': 15}),
    (2, 4, {'weight': 2, 'latency': 10}),
])

# Node and edge status (active/inactive)
node_status = {node: True for node in network.nodes}
edge_status = {edge: True for edge in network.edges}

@app.route('/get_network', methods=['GET'])
def get_network():
    # Filter out inactive nodes
    active_nodes = [node for node, status in node_status.items() if status]
    
    # Filter out edges where either source or target is inactive
    active_edges = [
        {'source': u, 'target': v, 'weight': data['weight'], 'latency': data['latency']}
        for u, v, data in network.edges(data=True)
        if u in active_nodes and v in active_nodes
    ]
    
    return jsonify({
        "nodes": [{"id": node} for node in active_nodes],
        "edges": active_edges,
        "metrics": {
            "packet_loss": random.uniform(0, 5),  # Simulated packet loss percentage
            "jitter": random.uniform(0, 10),  # Simulated jitter in milliseconds
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
def reroute():
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

    # Find shortest path
    try:
        path = nx.shortest_path(active_network, source=source, target=target, weight='weight')
        return jsonify({"status": "success", "path": path})
    except nx.NetworkXNoPath:
        return jsonify({"status": "error", "message": "No path available"})

if __name__ == '__main__':
    app.run(debug=True)

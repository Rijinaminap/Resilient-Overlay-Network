from flask import Flask, jsonify, request
import networkx as nx
import random
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
# Create a sample network topology
network = nx.Graph()
network.add_edges_from([
    (1, 2, {'weight': 1}),
    (2, 3, {'weight': 2}),
    (3, 4, {'weight': 1}),
    (1, 4, {'weight': 3}),
    (2, 4, {'weight': 2}),
])

# Node status (active/inactive)
node_status = {node: True for node in network.nodes}

@app.route('/get_network', methods=['GET'])
def get_network():
    edges = [{'source': u, 'target': v, 'weight': data['weight']}
             for u, v, data in network.edges(data=True)]
    return jsonify({"nodes": list(network.nodes), "edges": edges, "status": node_status})

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

    # Remove failed nodes
    active_network = network.copy()
    for node, status in node_status.items():
        if not status:
            active_network.remove_node(node)

    # Find shortest path
    try:
        path = nx.shortest_path(active_network, source=source, target=target, weight='weight')
        return jsonify({"status": "success", "path": path})
    except nx.NetworkXNoPath:
        return jsonify({"status": "error", "message": "No path available"})

if __name__ == '__main__':
    app.run(debug=True)

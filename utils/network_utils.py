import networkx as nx
import matplotlib.pyplot as plt
import asyncio
import time

# Initialize global variables for metrics
latency_total = 0
packet_loss = 0
successful_transmissions = 0
recovery_time_total = 0
transmission_attempts = 0

# Step 1: Create a Simple Network Graph
def create_network():
    G = nx.Graph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'D', weight=4)
    G.add_edge('C', 'D', weight=3)
    G.add_edge('D', 'F', weight=1)
    G.add_edge('E', 'F', weight=1)
    G.add_edge('A', 'F', weight=5)
    return G

# Step 2: Visualize the Network Graph
def draw_network(G):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue')
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

# Step 3: Simulate Node Failures
def simulate_failure(G, failed_nodes):
    for node in failed_nodes:
        if node in G:
            G.remove_node(node)
            print(f"Node {node} failed and was removed.")

# Step 4: Implement Rerouting with Shortest Path
def reroute(G, source, target):
    try:
        path = nx.shortest_path(G, source=source, target=target, weight='weight')
        print(f"Path from {source} to {target}: {path}")
        return path
    except nx.NetworkXNoPath:
        print(f"No path from {source} to {target}.")
        return None

# Step 5: Simulate Heartbeats to Monitor Nodes
async def heartbeat(node, neighbors):
    for _ in range(10):  # Limit the number of heartbeats
        print(f"Node {node}: Sending heartbeat to {neighbors}")
        await asyncio.sleep(1)
    print(f"Heartbeat for node {node} completed.")

# Step 6: Monitor Network for Failures
async def monitor_network(G, failed_nodes):
    for _ in range(10):  # Limit the number of monitoring checks
        for node in list(G.nodes):
            if node in failed_nodes:
                print(f"Node {node} has failed!")
                G.remove_node(node)
                failed_nodes.remove(node)
        await asyncio.sleep(1)
    print("Network monitoring completed.")

# Step 7: Simulate Data Transmission and Log Metrics
async def transmit_data(G, source, target):
    global latency_total, packet_loss, successful_transmissions, recovery_time_total, transmission_attempts

    for _ in range(5):  # Limit the number of data transmission attempts
        transmission_attempts += 1
        start_time = time.time()
        path = reroute(G, source, target)

        if path:
            # Simulate data transmission
            end_time = time.time()
            latency = end_time - start_time
            latency_total += latency
            successful_transmissions += 1
            print(f"Transmitting data from {source} to {target} via {path}, Latency: {latency:.2f} seconds")
        else:
            packet_loss += 1
            print(f"Transmission failed from {source} to {target} due to no available path.")

        await asyncio.sleep(3)
    
    # Log metrics after all transmission attempts
    log_metrics()

def log_metrics():
    global latency_total, packet_loss, successful_transmissions, recovery_time_total, transmission_attempts

    if successful_transmissions > 0:
        avg_latency = latency_total / successful_transmissions
    else:
        avg_latency = 0

    packet_loss_percentage = (packet_loss / transmission_attempts) * 100 if transmission_attempts > 0 else 0
    avg_recovery_time = recovery_time_total / successful_transmissions if successful_transmissions > 0 else 0

    print(f"--- Metrics ---")
    print(f"Average Latency: {avg_latency:.2f} seconds")
    print(f"Packet Loss: {packet_loss_percentage:.2f}%")
    print(f"Successful Transmissions: {successful_transmissions}/{transmission_attempts}")
    print(f"Average Recovery Time: {avg_recovery_time:.2f} seconds")


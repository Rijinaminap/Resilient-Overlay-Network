import networkx as nx
import os
import asyncio

# ------------- STEP 1: CREATE NETWORK GRAPH -------------
def create_network():
    """Create the network graph."""
    G = nx.Graph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'D', weight=1)
    G.add_edge('C', 'D', weight=1)
    G.add_edge('D', 'E', weight=1)
    return G

def draw_network(G):
    """Visualize the network graph."""
    import matplotlib.pyplot as plt

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue')
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

# ------------- STEP 2: FILE HANDLING -------------
def get_file_size(file_path):
    """Get the size of the file in KB."""
    return os.path.getsize(file_path) / 1024  # Size in KB

def read_file(file_path, chunk_size_kb=100):
    """
    Read the file in chunks to simulate packets.
    Each chunk is of size `chunk_size_kb`.
    """
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size_kb * 1024):  # Read chunk in bytes
            yield chunk

# ------------- STEP 3: NETWORK REROUTING -------------
def reroute(G, source, target):
    """
    Use shortest path algorithm to find a path from source to target.
    """
    try:
        path = nx.shortest_path(G, source=source, target=target, weight='weight')
        print(f"Path from {source} to {target}: {path}")
        return path
    except nx.NetworkXNoPath:
        print(f"No path from {source} to {target}.")
        return None

# ------------- STEP 4: FAILURE SIMULATION -------------
def simulate_failure(G, failed_nodes):
    """
    Simulate node or link failures by removing nodes from the graph.
    """
    for node in failed_nodes:
        if node in G:
            G.remove_node(node)
            print(f"Node {node} failed and was removed.")

# ------------- STEP 5: ASYNCHRONOUS DATA TRANSMISSION -------------
async def transmit_data_from_file(G, source, target, file_path):
    """
    Simulate transmitting data (file) from source to target.
    """
    total_data_transferred = 0
    total_chunks = 0

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    file_size_kb = get_file_size(file_path)
    print(f"File size: {file_size_kb:.2f} KB")

    for chunk in read_file(file_path):
        total_chunks += 1
        chunk_size_kb = len(chunk) / 1024
        total_data_transferred += chunk_size_kb

        path = reroute(G, source, target)
        if path:
            print(f"Transmitting chunk {total_chunks} of size {chunk_size_kb:.2f} KB via path: {path}")
        else:
            print(f"Transmission failed for chunk {total_chunks}. No available path.")
            break

        await asyncio.sleep(1)  # Simulate time taken for transmission

    print(f"Total chunks transmitted: {total_chunks}")
    print(f"Total data transmitted: {total_data_transferred:.2f} KB")

# ------------- STEP 6: METRICS LOGGING -------------
def log_metrics(file_path, total_data_transferred, failed_nodes):
    """
    Log performance metrics to a file.
    """
    with open("metrics.log", "w") as log_file:
        log_file.write("Resilient Overlay Network Metrics\n")
        log_file.write(f"File: {file_path}\n")
        log_file.write(f"Total Data Transferred: {total_data_transferred:.2f} KB\n")
        log_file.write(f"Failed Nodes: {', '.join(failed_nodes)}\n")
        log_file.write("End of metrics\n")

# ------------- STEP 7: MAIN PROGRAM -------------
async def main():
    """
    Main program to run the simulation.
    """
    G = create_network()
    draw_network(G)

    # File to transfer
    file_path = "C:\\Users\\ajnap\\OneDrive\\Desktop\\NOTES\\ACN\\2102_355_1253_3_zigbee.pdf"
  # Provide the path to your file
    source = 'A'
    target = 'E'
    failed_nodes = ['B']

    print("Simulating failures...")
    simulate_failure(G, failed_nodes)

    print("Starting data transmission...")
    await transmit_data_from_file(G, source, target, file_path)

    # Log metrics
    total_data_transferred = get_file_size(file_path)  # Assuming full file transfer for simplicity
    log_metrics(file_path, total_data_transferred, failed_nodes)

# Run the program
if __name__ == "__main__":
    asyncio.run(main())

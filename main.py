import networkx as nx
import matplotlib.pyplot as plt
import asyncio
import time
from utils.network_utils import create_network, draw_network, simulate_failure, reroute, heartbeat, monitor_network, transmit_data, log_metrics

# Step 1: Create the Network
def main():
    G = create_network()  # Create the graph
    
    # Step 2: Visualize the Network
    print("Initial Network:")
    draw_network(G)  # Draw initial network graph
    
    # Step 3: Simulate Node Failures
    failed_nodes = ['B','D']
    simulate_failure(G, failed_nodes)
    draw_network(G)  # Draw the network after failures
    
    # Step 4: Reroute Example
    reroute(G, 'A', 'E')  # Try to find a new path after failures
    
    # Step 5: Simulate Asynchronous Failure Detection & Data Transmission with Metrics Calculation
    asyncio.run(main_async(G, failed_nodes))

async def main_async(G, failed_nodes):
    # Start heartbeats and network monitoring in the background
    asyncio.create_task(heartbeat('A', list(G.neighbors('A'))))
    asyncio.create_task(monitor_network(G, failed_nodes))
    
    # Start transmission with metrics logging
    await asyncio.create_task(transmit_data(G, 'A', 'E'))
    
    # Run for a limited time (10 seconds)
    await asyncio.sleep(10)  # Run the simulation for 10 seconds
    print("Simulation finished.")

if __name__ == "__main__":
    main()

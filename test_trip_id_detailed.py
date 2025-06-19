#!/usr/bin/env python3
"""
Detailed test script for trip_id functionality in Pandana
This test demonstrates real usage of trip_id feature
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to Python path to import pandana
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pandana
except ImportError:
    print("Pandana not found. Please install it first.")
    sys.exit(1)

def create_detailed_test_network():
    """Create a more complex test network with realistic trip_ids"""
    
    # Create nodes representing bus stops
    nodes = pd.DataFrame({
        'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        'y': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    }, index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    # Create edges with different trip_ids representing different bus routes
    # Route 101: stops 1-9 (9 edges)
    route_101 = pd.DataFrame({
        'from': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'to': [2, 3, 4, 5, 6, 7, 8, 9, 10],
        'distance': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        'trip_id': [101, 101, 101, 101, 101, 101, 101, 101, 101]
    })
    
    # Route 201: express route (5 edges)
    route_201 = pd.DataFrame({
        'from': [1, 3, 5, 7, 9],
        'to': [3, 5, 7, 9, 10],
        'distance': [1.5, 1.5, 1.5, 1.5, 1.5],
        'trip_id': [201, 201, 201, 201, 201]
    })
    
    # Route 301: parallel route (5 edges)
    route_301 = pd.DataFrame({
        'from': [2, 4, 6, 8, 10],
        'to': [4, 6, 8, 10, 9],
        'distance': [1.2, 1.2, 1.2, 1.2, 1.2],
        'trip_id': [301, 301, 301, 301, 301]
    })
    
    # Route 401: diagonal route (6 edges)
    route_401 = pd.DataFrame({
        'from': [1, 2, 4, 6, 8, 10],
        'to': [2, 4, 6, 8, 10, 9],
        'distance': [1.3, 1.3, 1.3, 1.3, 1.3, 1.3],
        'trip_id': [401, 401, 401, 401, 401, 401]
    })
    
    # Combine all routes
    edges = pd.concat([route_101, route_201, route_301, route_401], ignore_index=True)
    
    return nodes, edges

def test_trip_id_functionality():
    """Test the trip_id functionality with detailed examples"""
    
    print("=" * 60)
    print("DETAILED TRIP_ID FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Create test network
    print("\n1. Creating detailed test network...")
    nodes, edges = create_detailed_test_network()
    
    print(f"   Nodes: {len(nodes)} (bus stops)")
    print(f"   Edges: {len(edges)} (route segments)")
    print(f"   Unique trip_ids: {edges['trip_id'].unique()}")
    
    # Create network
    network = pandana.Network(
        nodes['x'], 
        nodes['y'], 
        edges['from'], 
        edges['to'], 
        edges[['distance']]
    )
    
    # Set trip_ids
    print("\n2. Setting trip_ids for the network...")
    network.set_trip_ids(edges['trip_id'])
    print("   ✓ Trip IDs set successfully")
    
    # Test different scenarios
    print("\n3. Testing different path scenarios:")
    
    # Scenario 1: Direct route (should use Route 101)
    print("\n   Scenario 1: Direct route (Stop 1 → Stop 5)")
    origins = [1]
    destinations = [5]
    
    # Get node path
    node_paths = network.shortest_paths(origins, destinations)
    print(f"   Node path: {node_paths[0]}")
    
    # Get trip_id path
    trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
    print(f"   Trip path: {trip_paths[0]}")
    print(f"   Routes used: {list(set(trip_paths[0]))}")
    
    # Scenario 2: Express route (should use Route 201)
    print("\n   Scenario 2: Express route (Stop 1 → Stop 9)")
    origins = [1]
    destinations = [9]
    
    node_paths = network.shortest_paths(origins, destinations)
    print(f"   Node path: {node_paths[0]}")
    
    trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
    print(f"   Trip path: {trip_paths[0]}")
    print(f"   Routes used: {list(set(trip_paths[0]))}")
    
    # Scenario 3: Multiple paths
    print("\n   Scenario 3: Multiple paths analysis")
    origins = [1, 2, 3]
    destinations = [8, 9, 10]
    
    node_paths = network.shortest_paths(origins, destinations)
    trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
    
    for i, (origin, dest) in enumerate(zip(origins, destinations)):
        print(f"   Path {i+1}: Stop {origin} → Stop {dest}")
        print(f"     Nodes: {node_paths[i]}")
        print(f"     Routes: {trip_paths[i]}")
        print(f"     Unique routes: {list(set(trip_paths[i]))}")
    
    # Scenario 4: Route analysis
    print("\n   Scenario 4: Route usage analysis")
    all_trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
    
    # Count route usage
    route_usage = {}
    for path in all_trip_paths:
        for route in path:
            route_usage[route] = route_usage.get(route, 0) + 1
    
    print("   Route usage statistics:")
    for route, count in sorted(route_usage.items()):
        print(f"     Route {route}: used {count} times")
    
    # Test single path method
    print("\n5. Testing single path method:")
    single_node_path = network.shortest_path(1, 10)
    print(f"   Single path (nodes): {single_node_path}")
    
    # Test distances
    print("\n6. Testing path distances:")
    distances = network.shortest_path_lengths(origins, destinations)
    for i, (origin, dest, dist) in enumerate(zip(origins, destinations, distances)):
        print(f"   Distance {i+1}: Stop {origin} → Stop {dest} = {dist:.2f}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    return network, nodes, edges

def demonstrate_real_world_usage():
    """Demonstrate how this could be used in real-world scenarios"""
    
    print("\n" + "=" * 60)
    print("REAL-WORLD USAGE DEMONSTRATION")
    print("=" * 60)
    
    network, nodes, edges = test_trip_id_functionality()
    
    print("\n Example: Public Transportation Analysis")
    print("   This could be used to analyze:")
    print("   • Which bus routes are most efficient")
    print("   • Route optimization for passengers")
    print("   • Service frequency analysis")
    print("   • Transfer point identification")
    
    print("\n Example: Route Planning")
    print("   • Find optimal route using specific bus lines")
    print("   • Minimize transfers between routes")
    print("   • Consider route reliability and frequency")
    
    print("\n Example: Data Analysis")
    print("   • Count route usage in shortest paths")
    print("   • Identify most popular routes")
    print("   • Analyze route efficiency")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    demonstrate_real_world_usage() 
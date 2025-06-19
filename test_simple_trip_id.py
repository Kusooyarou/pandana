#!/usr/bin/env python3
"""
Simple test for debugging trip_id functionality
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pandana
except ImportError:
    print("Pandana not found. Please install it first.")
    sys.exit(1)

def test_simple_network():
    """Test with a very simple network"""
    
    print("Creating simple test network...")
    
    # Simple 3-node network
    nodes = pd.DataFrame({
        'x': [0, 1, 2],
        'y': [0, 1, 0]
    }, index=[1, 2, 3])
    
    # Simple edges with clear trip_ids
    edges = pd.DataFrame({
        'from': [1, 2],
        'to': [2, 3],
        'distance': [1.0, 1.0],
        'trip_id': [101, 102]
    })
    
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")
    print(f"Trip IDs: {edges['trip_id'].tolist()}")
    
    # Create network
    network = pandana.Network(
        nodes['x'], 
        nodes['y'], 
        edges['from'], 
        edges['to'], 
        edges[['distance']]
    )
    
    # Set trip_ids
    print("\nSetting trip_ids...")
    network.set_trip_ids(edges['trip_id'])
    
    # Test path
    print("\nTesting path from 1 to 3...")
    origins = [1]
    destinations = [3]
    
    # Get node path
    node_paths = network.shortest_paths(origins, destinations)
    print(f"Node path: {node_paths[0]}")
    
    # Get trip_id path
    print("\nCalling shortest_paths with trip_id=True...")
    try:
        trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
        print(f"Python received trip_paths: {trip_paths}")
        print(f"Trip path: {trip_paths[0]}")
        print(f"Trip path type: {type(trip_paths[0])}")
        print(f"Trip path length: {len(trip_paths[0])}")
        if len(trip_paths[0]) > 0:
            print(f"Trip path content: {list(trip_paths[0])}")
    except Exception as e:
        print(f"Error calling shortest_paths with trip_id=True: {e}")
        import traceback
        traceback.print_exc()
    
    # Test single path
    print("\nTesting single path...")
    single_path = network.shortest_path(1, 3)
    print(f"Single path: {single_path}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_simple_network() 
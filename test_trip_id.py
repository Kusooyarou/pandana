#!/usr/bin/env python3
"""
Test script for trip_id functionality in Pandana
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

def create_test_network():
    """Create a simple test network with trip_ids"""
    
    # Create nodes
    nodes = pd.DataFrame({
        'x': [0, 1, 2, 3, 4],
        'y': [0, 1, 0, 1, 0]
    }, index=[1, 2, 3, 4, 5])
    
    # Create edges with trip_ids
    edges = pd.DataFrame({
        'from': [1, 2, 3, 4, 1, 3],
        'to': [2, 3, 4, 5, 3, 5],
        'distance': [1.0, 1.0, 1.0, 1.0, 1.5, 1.5],
        'trip_id': [101, 102, 103, 104, 201, 202]  # Different trip_ids for different routes
    })
    
    return nodes, edges

def test_trip_id_functionality():
    """Test the new trip_id functionality"""
    
    print("Creating test network...")
    nodes, edges = create_test_network()
    
    # Create network
    network = pandana.Network(
        nodes['x'], 
        nodes['y'], 
        edges['from'], 
        edges['to'], 
        edges[['distance']]
    )
    
    print("Setting trip_ids...")
    network.set_trip_ids(edges['trip_id'])
    
    # Test shortest paths with nodes (original functionality)
    print("\nTesting shortest paths with nodes:")
    origins = [1, 1]
    destinations = [5, 3]
    
    node_paths = network.shortest_paths(origins, destinations)
    print(f"Node paths: {node_paths}")
    
    # Test shortest paths with trip_ids (new functionality)
    print("\nTesting shortest paths with trip_ids:")
    trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
    print(f"Trip paths: {trip_paths}")
    
    # Test single path
    print("\nTesting single path:")
    single_node_path = network.shortest_path(1, 5)
    print(f"Single node path: {single_node_path}")
    
    # Test error handling
    print("\nTesting error handling:")
    try:
        # This should raise an error if trip_ids are not set
        network2 = pandana.Network(
            nodes['x'], 
            nodes['y'], 
            edges['from'], 
            edges['to'], 
            edges[['distance']]
        )
        network2.shortest_paths([1], [5], trip_id=True)
    except ValueError as e:
        print(f"Expected error: {e}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_trip_id_functionality() 
# Trip ID Support in Pandana

This document describes the new trip_id functionality added to Pandana for supporting public transportation route analysis.

## Overview

The trip_id feature allows you to analyze shortest paths not just by nodes, but by transportation routes (trip_ids). This is particularly useful for public transportation networks where edges are grouped into routes.

## New Features

### 1. Setting Trip IDs

```python
# Create network as usual
network = pandana.Network(nodes['x'], nodes['y'], edges['from'], edges['to'], edges[['distance']])

# Set trip_ids for edges
network.set_trip_ids(edges['trip_id'])
```

### 2. Shortest Paths with Trip IDs

```python
# Original functionality - returns node paths
node_paths = network.shortest_paths(origins, destinations)

# New functionality - returns trip_id paths
trip_paths = network.shortest_paths(origins, destinations, trip_id=True)
```

## API Changes

### Network Class

#### New Method: `set_trip_ids(trip_ids)`
- **Parameters:**
  - `trip_ids`: pandas.Series or array-like
    - Trip IDs corresponding to each edge in the network
    - Must have the same length as the number of edges
- **Returns:** None
- **Raises:** ValueError if length doesn't match number of edges

#### Updated Method: `shortest_paths(nodes_a, nodes_b, imp_name=None, trip_id=False)`
- **New Parameters:**
  - `trip_id`: bool, optional (default: False)
    - If True, returns trip_ids instead of node paths
    - Requires trip_ids to be set using set_trip_ids() method
- **Returns:**
  - If `trip_id=False`: List of node arrays (original behavior)
  - If `trip_id=True`: List of trip_id arrays

## Example Usage

```python
import pandas as pd
import pandana

# Create sample data
nodes = pd.DataFrame({
    'x': [0, 1, 2, 3, 4],
    'y': [0, 1, 0, 1, 0]
}, index=[1, 2, 3, 4, 5])

edges = pd.DataFrame({
    'from': [1, 2, 3, 4, 1, 3],
    'to': [2, 3, 4, 5, 3, 5],
    'distance': [1.0, 1.0, 1.0, 1.0, 1.5, 1.5],
    'trip_id': [101, 102, 103, 104, 201, 202]
})

# Create network
network = pandana.Network(
    nodes['x'], 
    nodes['y'], 
    edges['from'], 
    edges['to'], 
    edges[['distance']]
)

# Set trip_ids
network.set_trip_ids(edges['trip_id'])

# Get node paths (original functionality)
node_paths = network.shortest_paths([1, 1], [5, 3])
print("Node paths:", node_paths)
# Output: [array([1, 2, 3, 4, 5]), array([1, 2, 3])]

# Get trip_id paths (new functionality)
trip_paths = network.shortest_paths([1, 1], [5, 3], trip_id=True)
print("Trip paths:", trip_paths)
# Output: [array([101, 102, 103, 104]), array([101, 102])]
```

## Error Handling

The implementation includes proper error handling:

```python
# This will raise an error if trip_ids are not set
try:
    network.shortest_paths([1], [5], trip_id=True)
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: trip_id=True requires trip_ids to be set using set_trip_ids() method
```

## Implementation Details

### C++ Level Changes

1. **EdgeData Structure**: Added `trip_id` field to store route identifiers
2. **Graphalg Class**: Added support for trip_id storage and retrieval
3. **Accessibility Class**: Added new methods for trip_id path computation
4. **Contraction Hierarchies**: Extended to support trip_id extraction during path unpacking

### Python Level Changes

1. **Network Class**: Added `trip_ids` field and `set_trip_ids()` method
2. **shortest_paths()**: Extended with `trip_id` parameter
3. **Cython Interface**: Added new methods for trip_id path computation

## Backward Compatibility

All changes are backward compatible:
- Existing code continues to work without modification
- New functionality is opt-in via the `trip_id` parameter
- Default behavior remains unchanged

## Testing

Run the test script to verify functionality:

```bash
python test_trip_id.py
```

## Performance Considerations

- Trip ID functionality adds minimal overhead when not used
- Memory usage increases slightly due to trip_id storage
- Path computation performance remains the same
- Trip ID extraction adds small computational cost during path unpacking

## Future Enhancements

Potential future improvements:
1. Support for multiple trip_ids per edge
2. Trip_id-based aggregation functions
3. Trip_id-aware accessibility calculations
4. Integration with GTFS data formats 
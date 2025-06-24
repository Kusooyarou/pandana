#cython: language_level=3

cimport cython
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.pair cimport pair

import numpy as np
import sys
NODE_ID_DTYPE = np.int32 if sys.platform.startswith('win') else np.int64
cimport numpy as np

# resources
# http://cython.readthedocs.io/en/latest/src/userguide/wrapping_CPlusPlus.html
# http://www.birving.com/blog/2014/05/13/passing-numpy-arrays-between-python-and/


cdef extern from "accessibility.h" namespace "MTC::accessibility":
    cdef cppclass Accessibility:
        Accessibility(int, vector[vector[int]], vector[vector[double]], bool) except +
        vector[string] aggregations
        vector[string] decays
        void initializeCategory(double, int, string, vector[int])
        pair[vector[vector[double]], vector[vector[int]]] findAllNearestPOIs(
            float, int, string, int)
        void initializeAccVar(string, vector[int], vector[double])
        vector[double] getAllAggregateAccessibilityVariables(
            float, string, string, string, int)
        vector[int] Route(int, int, int)
        vector[vector[int]] Routes(vector[int], vector[int], int)
        vector[int] RouteWithTripIds(int, int, int)
        vector[vector[int]] RoutesWithTripIds(vector[int], vector[int], int)
        double Distance(int, int, int)
        vector[double] Distances(vector[int], vector[int], int)
        vector[vector[pair[int, float]]] Range(vector[int], float, int, vector[int])
        void precomputeRangeQueries(double)
        void set_trip_ids(vector[int] trip_ids)


cdef np.ndarray[double] convert_vector_to_array_dbl(vector[double] vec):
    cdef np.ndarray arr = np.zeros(len(vec), dtype="double")
    for i in range(len(vec)):
        arr[i] = vec[i]
    return arr


cdef np.ndarray[double, ndim = 2] convert_2D_vector_to_array_dbl(
        vector[vector[double]] vec):
    cdef np.ndarray arr = np.empty_like(vec, dtype="double")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            arr[i][j] = vec[i][j]
    return arr


cdef np.ndarray[int, ndim = 2] convert_2D_vector_to_array_int(
        vector[vector[int]] vec):
    cdef np.ndarray arr = np.empty_like(vec, dtype="int")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            arr[i][j] = vec[i][j]
    return arr


cdef class cyaccess:
    cdef Accessibility * access

    def __cinit__(
        self,
        np.ndarray[np.int32_t, ndim=1] node_ids,
        np.ndarray[double, ndim=2] node_xys,
        np.ndarray[np.int32_t, ndim=2] edges,
        np.ndarray[double, ndim=2] edge_weights,
        bool twoway=True
    ):
        """
        node_ids: vector of node identifiers
        node_xys: the spatial locations of the same nodes
        edges: a pair of node ids which comprise each edge
        edge_weights: the weights (impedances) that apply to each edge
        twoway: whether the edges should all be two-way or whether they
            are directed from the first to the second node
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG __cinit__ node_ids dtype: {getattr(node_ids, "dtype", None)}\n')
        #     f.write(f'CYTHON DEBUG __cinit__ edges dtype: {getattr(edges, "dtype", None)}\n')
        node_ids = np.asarray(node_ids, dtype=NODE_ID_DTYPE)
        edges = np.asarray(edges, dtype=NODE_ID_DTYPE)
        self.access = new Accessibility(len(node_ids), edges, edge_weights, twoway)

    def __dealloc__(self):
        del self.access

    def initialize_category(
        self,
        double maxdist,
        int maxitems,
        string category,
        np.ndarray[np.int32_t, ndim=1] node_ids
    ):
        """
        maxdist - the maximum distance that will later be used in
            find_all_nearest_pois
        maxitems - the maximum number of items that will later be requested
            in find_all_nearest_pois
        category - the category name
        node_ids - an array of nodeids which are locations where this poi occurs
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG initialize_category node_ids dtype: {getattr(node_ids, "dtype", None)}\n')
        node_ids = np.asarray(node_ids, dtype=NODE_ID_DTYPE)
        self.access.initializeCategory(maxdist, maxitems, category, node_ids)

    def find_all_nearest_pois(
        self,
        double radius,
        int num_of_pois,
        string category,
        int impno=0
    ):
        """
        radius - search radius
        num_of_pois - number of pois to search for
        category - the category name
        impno - the impedance id to use
        return_nodeids - whether to return the nodeid locations of the nearest
            not just the distances
        """
        ret = self.access.findAllNearestPOIs(radius, num_of_pois, category, impno)

        return convert_2D_vector_to_array_dbl(ret.first),\
            convert_2D_vector_to_array_int(ret.second)

    def initialize_access_var(
        self,
        string category,
        np.ndarray[np.int32_t, ndim=1] node_ids,
        np.ndarray[double, ndim=1] values
    ):
        """
        category - category name
        node_ids: vector of node identifiers
        values: vector of values that are location at the nodes
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG initialize_access_var node_ids dtype: {getattr(node_ids, "dtype", None)}\n')
        node_ids = np.asarray(node_ids, dtype=NODE_ID_DTYPE)
        values = np.asarray(values, dtype=np.float64)
        self.access.initializeAccVar(category, node_ids, values)

    def get_available_aggregations(self):
        return self.access.aggregations

    def get_available_decays(self):
        return self.access.decays

    def get_all_aggregate_accessibility_variables(
        self,
        double radius,
        category,
        aggtyp,
        decay,
        int impno=0,
    ):
        """
        radius - search radius
        category - category name
        aggtyp - aggregation type, see docs
        decay - decay type, see docs
        impno - the impedance id to use
        """
        ret = self.access.getAllAggregateAccessibilityVariables(
            radius, category, aggtyp, decay, impno)

        return convert_vector_to_array_dbl(ret)

    def shortest_path(self, int srcnode, int destnode, int impno=0):
        """
        srcnode - node id origin
        destnode - node id destination
        impno - the impedance id to use
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG shortest_path srcnode type: {type(srcnode)}, destnode type: {type(destnode)}\n')
        srcnode = NODE_ID_DTYPE(srcnode)
        destnode = NODE_ID_DTYPE(destnode)
        return self.access.Route(srcnode, destnode, impno)

    def shortest_paths(self, srcnodes, destnodes, int impno=0):
        """
        srcnodes - node ids of origins
        destnodes - node ids of destinations
        impno - impedance id
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG shortest_paths srcnodes dtype: {getattr(srcnodes, "dtype", None)}\n')
        #     f.write(f'CYTHON DEBUG shortest_paths destnodes dtype: {getattr(destnodes, "dtype", None)}\n')
        srcnodes = np.asarray(srcnodes, dtype=NODE_ID_DTYPE)
        destnodes = np.asarray(destnodes, dtype=NODE_ID_DTYPE)
        return self.access.Routes(srcnodes, destnodes, impno)

    def shortest_paths_with_trip_ids(self, srcnodes, destnodes, int impno=0):
        """
        srcnodes - node ids of origins
        destnodes - node ids of destinations
        impno - impedance id
        Returns trip_ids instead of node paths
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG shortest_paths_with_trip_ids srcnodes dtype: {getattr(srcnodes, "dtype", None)}\n')
        #     f.write(f'CYTHON DEBUG shortest_paths_with_trip_ids destnodes dtype: {getattr(destnodes, "dtype", None)}\n')
        srcnodes = np.asarray(srcnodes, dtype=NODE_ID_DTYPE)
        destnodes = np.asarray(destnodes, dtype=NODE_ID_DTYPE)
        return self.access.RoutesWithTripIds(srcnodes, destnodes, impno)

    def shortest_path_distance(self, int srcnode, int destnode, int impno=0):
        """
        srcnode - node id origin
        destnode - node id destination
        impno - the impedance id to use
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG shortest_path_distance srcnode type: {type(srcnode)}, destnode type: {type(destnode)}\n')
        srcnode = NODE_ID_DTYPE(srcnode)
        destnode = NODE_ID_DTYPE(destnode)
        return self.access.Distance(srcnode, destnode, impno)

    def shortest_path_distances(self, srcnodes, destnodes, int impno=0):
        """
        srcnodes - node ids of origins
        destnodes - node ids of destinations
        impno - impedance id
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG shortest_path_distances srcnodes dtype: {getattr(srcnodes, "dtype", None)}\n')
        #     f.write(f'CYTHON DEBUG shortest_path_distances destnodes dtype: {getattr(destnodes, "dtype", None)}\n')
        srcnodes = np.asarray(srcnodes, dtype=NODE_ID_DTYPE)
        destnodes = np.asarray(destnodes, dtype=NODE_ID_DTYPE)
        return self.access.Distances(srcnodes, destnodes, impno)
    
    def precompute_range(self, double radius):
        self.access.precomputeRangeQueries(radius)

    def nodes_in_range(self, srcnodes, float radius, int impno, ext_ids):
        """
        srcnodes - node ids of origins
        radius - maximum range in which to search for nearby nodes
        impno - the impedance id to use
        ext_ids - all node ids in the network
        """
        # with open('debug.log', 'a') as f:
        #     f.write(f'CYTHON DEBUG nodes_in_range srcnodes dtype: {getattr(srcnodes, "dtype", None)}\n')
        #     f.write(f'CYTHON DEBUG nodes_in_range ext_ids dtype: {getattr(ext_ids, "dtype", None)}\n')
        srcnodes = np.asarray(srcnodes, dtype=NODE_ID_DTYPE)
        ext_ids = np.asarray(ext_ids, dtype=NODE_ID_DTYPE)
        return self.access.Range(srcnodes, radius, impno, ext_ids)

    def simple_test(self):
        return "test"

    def test_method(self):
        print("Test method works!")
        return True

    def set_trip_ids(self, np.ndarray[int] trip_ids):
        print(f"[CYTHON DEBUG] set_trip_ids called with {len(trip_ids)} trip_ids")
        # Simple implementation for now
        pass

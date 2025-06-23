#include "graphalg.h"
#include "accessibility.h"
#include "shared.h"
#include <math.h>

namespace MTC {
namespace accessibility {
Graphalg::Graphalg(
        int numnodes, vector< vector<int> > edges, vector<double> edgeweights,
        bool twoway) {
    this->numnodes = numnodes;
    this->edges_storage = edges;

    int num = omp_get_max_threads();
    
    FILE_LOG(logINFO) << "Generating contraction hierarchies with "
                      << num << " threads.\n";
    
    ch = CH::ContractionHierarchies(num);

    vector<CH::Node> nv;

    for (int i = 0 ; i < numnodes ; i++) {
        // CH allows you to pass in a node id, and an x and a y, and then
        // never uses it - to be clear, we don't pass it in anymore
        CH::Node n(i, 0, 0);
        nv.push_back(n);
    }

    FILE_LOG(logINFO) << "Setting CH node vector of size "
                      << nv.size() << "\n";
	
    ch.SetNodeVector(nv);

    vector<CH::Edge> ev;

    for (int i = 0 ; i < edges.size() ; i++) {
        CH::Edge e(edges[i][0], edges[i][1], i,
            edgeweights[i]*DISTANCEMULTFACT, true, twoway);
        ev.push_back(e);
    }

    FILE_LOG(logINFO) << "Setting CH edge vector of size "
                      << ev.size() << "\n";
    
    ch.SetEdgeVector(ev);
    ch.RunPreprocessing();
}

Graphalg::Graphalg(
        int numnodes, vector< vector<int> > edges, vector<double> edgeweights,
        vector<int> trip_ids, bool twoway) : numnodes(numnodes), trip_ids(trip_ids) {
    this->edges_storage = edges;

    int num = omp_get_max_threads();
    
    FILE_LOG(logINFO) << "Generating contraction hierarchies with "
                      << num << " threads.\n";
    
    ch = CH::ContractionHierarchies(num);

    vector<CH::Node> nv;

    for (int i = 0 ; i < numnodes ; i++) {
        // CH allows you to pass in a node id, and an x and a y, and then
        // never uses it - to be clear, we don't pass it in anymore
        CH::Node n(i, 0, 0);
        nv.push_back(n);
    }

    FILE_LOG(logINFO) << "Setting CH node vector of size "
                      << nv.size() << "\n";
	
    ch.SetNodeVector(nv);

    vector<CH::Edge> ev;

    for (int i = 0 ; i < edges.size() ; i++) {
        int trip_id = (i < trip_ids.size()) ? trip_ids[i] : -1;
        CH::Edge e(edges[i][0], edges[i][1], i,
            edgeweights[i]*DISTANCEMULTFACT, true, twoway, trip_id, i);
        ev.push_back(e);
    }

    FILE_LOG(logINFO) << "Setting CH edge vector of size "
                      << ev.size() << "\n";
    
    ch.SetEdgeVector(ev);
    ch.RunPreprocessing();
}

Graphalg::Graphalg(
    int numnodes,
    vector< vector<int> > edges, vector<double> edgeweights,
    bool twoway,
    class Accessibility* accessibility_ptr) : numnodes(numnodes), accessibility_ptr(accessibility_ptr) {
    
    this->edges_storage = edges;

    int num = omp_get_max_threads();
    
    FILE_LOG(logINFO) << "Generating contraction hierarchies with "
                      << num << " threads.\n";
    
    ch = CH::ContractionHierarchies(num);

    vector<CH::Node> nv;

    for (int i = 0 ; i < numnodes ; i++) {
        // CH allows you to pass in a node id, and an x and a y, and then
        // never uses it - to be clear, we don't pass it in anymore
        CH::Node n(i, 0, 0);
        nv.push_back(n);
    }

    FILE_LOG(logINFO) << "Setting CH node vector of size "
                      << nv.size() << "\n";
	
    ch.SetNodeVector(nv);

    vector<CH::Edge> ev;

    for (int i = 0 ; i < edges.size() ; i++) {
        CH::Edge e(edges[i][0], edges[i][1], i,
            edgeweights[i]*DISTANCEMULTFACT, true, twoway, -1, i);
        ev.push_back(e);
    }

    FILE_LOG(logINFO) << "Setting CH edge vector of size "
                      << ev.size() << "\n";
    
    ch.SetEdgeVector(ev);
    ch.RunPreprocessing();
}

std::vector<NodeID> Graphalg::Route(int src, int tgt, int threadNum) {
    std::vector<NodeID> ResultingPath;

    CH::Node src_node(src, 0, 0);
    CH::Node tgt_node(tgt, 0, 0);

    ch.computeShortestPath(
        src_node,
        tgt_node,
        ResultingPath,
        threadNum);

    return ResultingPath;
}

std::vector<int> Graphalg::RouteWithTripIds(int src, int tgt, int threadNum) {
    //std::cout << "DEBUG: RouteWithTripIds called with src=" << src << ", tgt=" << tgt << ", threadNum=" << threadNum << std::endl;
    
    std::vector<NodeID> ResultingPath;
    std::vector<int> ResultingTripIds;

    CH::Node src_node(src, 0, 0);
    CH::Node tgt_node(tgt, 0, 0);

    ch.computeShortestPath(
        src_node,
        tgt_node,
        ResultingPath,
        threadNum);

    // Debug info
    //std::cout << "DEBUG: After computeShortestPath, ResultingPath size = " << ResultingPath.size() << std::endl;
    if (ResultingPath.size() > 0) {
        //std::cout << "DEBUG: ResultingPath = [";
        for (size_t i = 0; i < ResultingPath.size(); ++i) {
            std::cout << ResultingPath[i];
            if (i + 1 < ResultingPath.size()) std::cout << ", ";
        }
        //std::cout << "]" << std::endl;
    }

    // Get trip_ids from accessibilityVars through accessibility_ptr
    std::vector<int> trip_ids;
    if (accessibility_ptr != nullptr) {
        //std::cout << "DEBUG: Looking for trip_ids in accessibilityVars" << std::endl;
        
        // Check if trip_ids are available in accessibilityVars
        auto trip_ids_iter = accessibility_ptr->accessibilityVars.find("trip_ids");
        if (trip_ids_iter != accessibility_ptr->accessibilityVars.end()) {
            const auto& trip_ids_vars = trip_ids_iter->second;
            //std::cout << "DEBUG: Found trip_ids in accessibilityVars, size = " << trip_ids_vars.size() << std::endl;

            // Convert accessibilityVars to vector<int> for easier access
            for (const auto& node_vars : trip_ids_vars) {
                for (const auto& var : node_vars) {
                    trip_ids.push_back(static_cast<int>(var));
                }
            }
            
            //std::cout << "DEBUG: Converted trip_ids size = " << trip_ids.size() << std::endl;
        } else {
            //std::cout << "DEBUG: trip_ids not found in accessibilityVars" << std::endl;
        }
    } else {
        //std::cout << "DEBUG: accessibility_ptr is null" << std::endl;
    }

    //FILE_LOG(logINFO) << "RouteWithTripIds: Path size = " << ResultingPath.size() << "\n";
    //FILE_LOG(logINFO) << "RouteWithTripIds: Edges storage size = " << edges_storage.size() << "\n";
    //FILE_LOG(logINFO) << "RouteWithTripIds: Trip IDs size = " << trip_ids.size() << "\n";

    // For each consecutive pair of nodes in the path, find the corresponding edge and its trip_id
    for (size_t i = 0; i < ResultingPath.size() - 1; ++i) {
        int from_node = ResultingPath[i];
        int to_node = ResultingPath[i + 1];
        
        //std::cout << "DEBUG: Looking for edge from " << from_node << " to " << to_node << std::endl;
        
        // Find the edge in edges_storage
        bool found = false;
        for (size_t j = 0; j < edges_storage.size(); ++j) {
            if (edges_storage[j][0] == from_node && edges_storage[j][1] == to_node) {
                int trip_id = (j < trip_ids.size()) ? trip_ids[j] : -1;
                //std::cout << "DEBUG: Found edge at index " << j << " with trip_id = " << trip_id << std::endl;
                ResultingTripIds.push_back(trip_id);
                found = true;
                break;
            }
        }
        
        if (!found) {
            //std::cout << "DEBUG: No matching edge found for " << from_node << " -> " << to_node << std::endl;
            ResultingTripIds.push_back(-1);
        }
    }

    //FILE_LOG(logINFO) << "RouteWithTripIds: Returning " << ResultingTripIds.size() << " trip IDs\n";
    std::string trip_ids_str = "[";
    for (size_t i = 0; i < ResultingTripIds.size(); ++i) {
        trip_ids_str += std::to_string(ResultingTripIds[i]);
        if (i + 1 < ResultingTripIds.size()) trip_ids_str += ", ";
    }
    trip_ids_str += "]";
    //FILE_LOG(logINFO) << "RouteWithTripIds: Trip ID path = " << trip_ids_str << "\n";

    //std::cout << "DEBUG: RouteWithTripIds returning trip_ids: " << trip_ids_str << std::endl;
    //std::cout << "DEBUG: ResultingTripIds size: " << ResultingTripIds.size() << std::endl;
    
    return ResultingTripIds;
}


double Graphalg::Distance(int src, int tgt, int threadNum) {
    CH::Node src_node(src, 0, 0);
    CH::Node tgt_node(tgt, 0, 0);

    unsigned int length = ch.computeLengthofShortestPath(
        src_node,
        tgt_node,
        threadNum);

    return static_cast<double>(length) / static_cast<double>(DISTANCEMULTFACT);
}


void Graphalg::Range(int src, double maxdist, int threadNum,
                     DistanceVec &ResultingNodes) {
    CH::Node src_node(src, 0, 0);

    std::vector<std::pair<NodeID, unsigned> > tmp;

    ch.computeReachableNodesWithin(
        src_node,
        maxdist*DISTANCEMULTFACT,
        tmp,
        threadNum);

    for (int i = 0 ; i < tmp.size() ; i++) {
        std::pair<NodeID, float> node;
        node.first = tmp[i].first;
        node.second = tmp[i].second/DISTANCEMULTFACT;
        ResultingNodes.push_back(node);
    }
}


DistanceMap
Graphalg::NearestPOI(const POIKeyType &category, int src, double maxdist, int number,
                     int threadNum) {
    DistanceMap dm;

    std::vector<CH::BucketEntry> ResultingNodes;
    ch.getNearestWithUpperBoundOnDistanceAndLocations(
        category,
        src,
        maxdist*DISTANCEMULTFACT,
        number,
        ResultingNodes,
        threadNum);

    for (int i = 0 ; i < ResultingNodes.size() ; i++) {
        dm[ResultingNodes[i].node] =
            static_cast<float>(ResultingNodes[i].distance) /
            static_cast<float>(DISTANCEMULTFACT);
    }

    return dm;
}

std::vector<std::vector<int>> Graphalg::RoutesWithTripIds(std::vector<int> sources, std::vector<int> targets, int threadNum) {
    size_t n = std::min(sources.size(), targets.size());
    std::vector<std::vector<int>> result(n);
    for (size_t i = 0; i < n; ++i) {
        result[i] = this->RouteWithTripIds(static_cast<int>(sources[i]), static_cast<int>(targets[i]), threadNum);
    }
    return result;
}
}  // namespace accessibility
}  // namespace MTC

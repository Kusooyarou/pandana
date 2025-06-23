#pragma once

#include <vector>
#include <map>
#include <utility>
#include "shared.h"
#include "contraction_hierarchies/src/libch.h"

typedef unsigned int NodeID;

#define DISTANCEMULTFACT 1000.0

namespace MTC {
namespace accessibility {

using std::vector;

typedef std::map<int, float> DistanceMap;
typedef std::vector<std::pair<NodeID, float> > DistanceVec;

class Graphalg {
 public:
    Graphalg(
        int numnodes,
        vector< vector<int> > edges, vector<double> edgeweights,
        bool twoway);

    Graphalg(
        int numnodes,
        vector< vector<int> > edges, vector<double> edgeweights,
        vector<int> trip_ids,
        bool twoway);

    Graphalg(
        int numnodes,
        vector< vector<int> > edges, vector<double> edgeweights,
        bool twoway,
        class Accessibility* accessibility_ptr);

    std::vector<NodeID> Route(int src, int tgt, int threadNum = 0);

    std::vector<int> RouteWithTripIds(int src, int tgt, int threadNum = 0);

    double Distance(int src, int tgt, int threadNum = 0);

    void Range(int src, double maxdist, int threadNum,
               DistanceVec &ResultingNodes);

    DistanceMap NearestPOI(const POIKeyType &category, int src, double maxdist,
                           int number, int threadNum = 0);

    void addPOIToIndex(const POIKeyType &category, int i) {
        ch.addPOIToIndex(category, i);
    }

    void initPOIIndex(const POIKeyType &category, double maxdist, int maxitems) {
        ch.createPOIIndex(category, maxdist*DISTANCEMULTFACT, maxitems);
    }

    void set_trip_ids(std::vector<int> trip_ids) {
        this->trip_ids = trip_ids;
    }

    int numnodes;
    CH::ContractionHierarchies ch;
    std::vector<int> trip_ids;
    std::vector<std::vector<int>> edges_storage;
    
    // Pointer to Accessibility for accessing accessibilityVars
    class Accessibility* accessibility_ptr;

    std::vector<std::vector<int>> RoutesWithTripIds(std::vector<int> sources, std::vector<int> targets, int threadNum = 0);
};
}  // namespace accessibility
}  // namespace MTC

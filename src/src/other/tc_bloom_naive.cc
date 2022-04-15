// Copyright (c) 2015, The Regents of the University of California (Regents)
// See LICENSE.txt for license details

#include <algorithm>
#include <cinttypes>
#include <iostream>
#include <vector>
#include <cstdio>
#include <cmath>

#include "../benchmark.h"
#include "../builder.h"
#include "../command_line.h"
#include "../graph.h"
#include "../pvector.h"
#include "../bloom_filter.hpp"


/*
GAP Benchmark Suite
Kernel: Triangle Counting (TC)
Author: Scott Beamer

Will count the number of triangles (cliques of size 3)

Requires input graph:
  - to be undirected
  - no duplicate edges (or else will be counted as multiple triangles)
  - neighborhoods are sorted by vertex identifiers

Other than symmetrizing, the rest of the requirements are done by SquishCSR
during graph building.

This implementation reduces the search space by counting each triangle only
once. A naive implementation will count the same triangle six times because
each of the three vertices (u, v, w) will count it in both ways. To count
a triangle only once, this implementation only counts a triangle if u > v > w.
Once the remaining unexamined neighbors identifiers get too big, it can break
out of the loop, but this requires that the neighbors to be sorted.

Another optimization this implementation has is to relabel the vertices by
degree. This is beneficial if the average degree is high enough and if the
degree distribution is sufficiently non-uniform. To decide whether or not
to relabel the graph, we use the heuristic in WorthRelabelling.
*/


using namespace std;

vector<bloom_filter> generate_filters(const double acc, const Graph &g){
  const int64_t n = g.num_nodes();
  int max_deg = -1;
  for(auto u = 0; u<n; u++){
    const auto deg_u = g.out_degree(u);
    if(deg_u > max_deg) max_deg=deg_u;
  }
  vector<bloom_filter> filters;
  filters.reserve(n);
  auto seed = random_device{}();
  for(NodeID u = 0; u<n; u++){
    bloom_parameters param;
    param.projected_element_count=(NodeID) max_deg;
    param.false_positive_probability=acc;
    param.random_seed=seed;
    param.compute_optimal_parameters();
    filters.push_back(bloom_filter(param));
    (filters[u]).insert(g.out_neigh(u).begin(), g.out_neigh(u).end());
  }
  return filters;
}

size_t OrderedCount(const double acc, const Graph &g, const vector<bloom_filter> &filters) {
  size_t total = 0;
  #pragma omp parallel for reduction(+ : total) schedule(dynamic, 64)
  for (NodeID u=0; u < g.num_nodes(); u++) {
    for (NodeID v : g.out_neigh(u)) {
      if (v > u) 
        break;
      total += filters[u].approximate_intersection_count(filters[v]);
//      auto it = g.out_neigh(u).begin();
//      for (NodeID w : g.out_neigh(v)) {
//        if (w > v)
//          break;
//        while (*it < w)
//          it++;
//        if (w == *it)
//          total++;
//      }
    }
  }
  return total/3;
}


// heuristic to see if sufficently dense power-law graph
bool WorthRelabelling(const Graph &g) {
  int64_t average_degree = g.num_edges() / g.num_nodes();
  if (average_degree < 10)
    return false;
  SourcePicker<Graph> sp(g);
  int64_t num_samples = min(int64_t(1000), g.num_nodes());
  int64_t sample_total = 0;
  pvector<int64_t> samples(num_samples);
  for (int64_t trial=0; trial < num_samples; trial++) {
    samples[trial] = g.out_degree(sp.PickNext());
    sample_total += samples[trial];
  }
  sort(samples.begin(), samples.end());
  double sample_average = static_cast<double>(sample_total) / num_samples;
  double sample_median = samples[num_samples/2];
  return sample_average / 1.3 > sample_median;
}


// uses heuristic to see if worth relabeling
size_t Hybrid(const double acc, const Graph &g, const vector<bloom_filter> filters) {
  return OrderedCount(acc, g,filters);
}


void PrintTriangleStats(const Graph &g, size_t total_triangles) {
  cout << total_triangles << " triangles" << endl;
}


// Compares with simple serial implementation that uses std::set_intersection

bool TCVerifier(const Graph &g, size_t test_total, const CLApp &cli) {
  size_t total = 0;
  vector<NodeID> intersection;
  intersection.reserve(g.num_nodes());
  for (NodeID u : g.vertices()) {
    for (NodeID v : g.out_neigh(u)) {
      auto new_end = set_intersection(g.out_neigh(u).begin(),
                                      g.out_neigh(u).end(),
                                      g.out_neigh(v).begin(),
                                      g.out_neigh(v).end(),
                                      intersection.begin());
      intersection.resize(new_end - intersection.begin());
      total += intersection.size();
    }
  }
  total = total / 6;  // each triangle was counted 6 times
  cout << "acc: " << (float)((float)test_total-total)/total*100  << "\% error: true " << total << " counted " << test_total << endl;
  return total == test_total;
}

int main(int argc, char* argv[]) {	
  CLBloomApp cli(argc, argv, "bloom triangle count");
  if (!cli.ParseArgs())
    return -1;
  Builder b(cli);
  Graph g = b.MakeGraph();
  if (g.directed()) {
    cout << "Input graph is directed but tc requires undirected" << endl;
    return -2;
  }
  cout << "Accuracy: " << (float) cli.accuracy() << endl;
  auto filters = generate_filters(cli.accuracy(), g);
  auto ct = [&cli, &filters] (const Graph &g) {
    return OrderedCount(cli.accuracy(), g, filters);
  };
  BenchmarkKernel(cli, g, ct, PrintTriangleStats, TCVerifier);
  filters.clear();
  return 0;
}

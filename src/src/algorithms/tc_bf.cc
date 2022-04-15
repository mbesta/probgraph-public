// Copyright (c) 2015, The Regents of the University of California (Regents)
// See LICENSE.txt for license details
#include <algorithm>
#include <cinttypes>
#include <iostream>
#include <vector>
#include <memory>
#include "../benchmark.h"
#include "../builder.h"
#include "../command_line.h"
#include "../graph.h"
#include "../pvector.h"
#include "../set_operation.hpp"
#include "../sets.hpp"
#include <sys/time.h>

using namespace std;


std::vector<NodeID*> addSets(vector<BloomSet<NodeID>*> &sets, const Graph &g, float tres, int& k_, int& m_) {
    cout << "threshold: " << tres << endl;
    int64_t max_degree = 0;
    for (NodeID u=0; u<g.num_nodes(); ++u) {
        max_degree = std::max(max_degree, g.out_degree(u));
    }
    cout << "max_degree: " << max_degree << endl;

    if (k_ <= 0 and m_ <= 0 ) std::cout<<"k and m will set automatically"<<std::endl;

    int m = m_, k=k_;

    if (m <= 0){
        m = max_degree * tres;
    }
    if (m<32) {
        m = 32;
    }

    if (k <= 0){
        if (max_degree!=0) {
            k = m/max_degree*0.69314718056; // m/n*ln(2)
        }
    }
    if (k<1) {
        k = 1;
    }

    cout << "m: " << m << endl;
    cout << "k: " << k << endl;
    k_ = k;
    m_ = m;
    struct timeval seed;
    gettimeofday(&seed, NULL);
    srand(seed.tv_usec);
    std::vector<uint32_t> seeds;
    for (int i = 0; i<k; i++) {
        seeds.push_back(rand());
    }


    std::vector<NodeID*> hstart; // Stores the end iterator to the range of neighbor vertices
    hstart.reserve(g.num_nodes());
    for (NodeID u = 0; u < g.num_nodes(); ++u) {
        NodeID* u_neigh = g.out_neigh(u).begin();
        int64_t u_deg = g.out_degree(u);
        NodeID* vcandidates_start; // The end iterator to the range of vertices added to the current bloomSet
        if (u_deg==0) {
        vcandidates_start=u_neigh; // No vertices to be added to bloomset
    } else {
        int oldind = 0;
        int ind = 0;
        while (ind < u_deg) {
            if (*(u_neigh+ind)>u) {
                break;
            } else {
                oldind = ind;
                ind = ((ind+1)<<1)-1; // 2x(ind+1) - 1
            }
        }
        int64_t* low = u_neigh + oldind;
        int64_t* high;
        if (ind<u_deg) {
            high = u_neigh + ind;
        }
        else {
            if (u > *(u_neigh + u_deg-1)) {
                high = u_neigh + u_deg;
            } else {
                high = u_neigh + u_deg-1;
            }
        }
        while (high>low) {
            int64_t* pivot = (low + (high-low)/2);
            if (*pivot<u) {
                low = pivot + 1;
            } else {
                high = pivot;
            }
        }
        vcandidates_start = high;
    }

    BloomSet<NodeID> * neigh = new BloomSet<NodeID>(g.out_neigh(u).begin(), vcandidates_start, m, k, seeds, g.num_nodes());

    sets.push_back(neigh);
    hstart.push_back(vcandidates_start);
    }
    return hstart;
}


size_t OrderedCount(const Graph &g, float tres, int k_, int m_, FILE *fp_tr, std::string graphName, int threads) {

    double tc_time = -1;
    double pp_time = -1;
    double approx_str_size = -1;
    double initial_csr_size = -1;
    int k_temp;
    int m_temp;

    int num_thresholds;
    float *thresholds;
    if (fp_tr != nullptr) {
        fscanf(fp_tr, "%d", &num_thresholds);
        printf("ooo Running for %d threshold values\n", num_thresholds);
        assert (num_thresholds >= 1);
        thresholds = (float *) malloc (sizeof(float) * num_thresholds);
        for (int i = 0; i < num_thresholds; i++)
            fscanf(fp_tr, "%f", &thresholds[i]);
    }
    else {
        num_thresholds = 1;
        thresholds = (float *) malloc (sizeof(float) * num_thresholds);
        thresholds[0] = tres;
    }

    for (int i = 0; i < num_thresholds; i++) {
        tres = thresholds[i];
        printf("ooo -------------------------------\n");
        printf("ooo Running for threshold: %f\n", tres);
        Timer t;
        vector<BloomSet<NodeID>*> sets;
        vector<NodeID*> hstart;
        t.Start();
        k_temp = k_;
        m_temp = m_;
        hstart = addSets(sets, g, tres, k_temp, m_temp);
        t.Stop();
        PrintTime("ooo Datastructure building", t.Seconds());

        pp_time = t.Seconds();

        size_t size = 0;
        for (int i = 0; i<g.num_nodes(); i++) {
            size+= sets[i]->total_size();
        }
        PrintTime("ooo Datastructure size", size);

        approx_str_size = size / (1024.0 * 1024.0); // MB
        initial_csr_size = g.getSize() / (1024.0 * 1024.0); //MB

        size_t total = 0;
        t.Start();
        #pragma omp parallel reduction(+:total)
        {
            #pragma omp for schedule(dynamic)
            for (NodeID u = 0; u < g.num_nodes(); ++u) {
                for (NodeID* vp = g.out_neigh(u).begin(); vp < hstart[u]; vp++) {
                    int n = (*sets[u]).intersect_count(*sets[*vp]);
                    total += n;
                }
            }
        }
        t.Stop();
        PrintTime("ooo Intersection time", t.Seconds());
        tc_time = t.Seconds();

        for(auto set:sets) {
            delete set;
        }
        sets.clear();
        sets.shrink_to_fit();
        hstart.clear();
        hstart.shrink_to_fit();
        std::cout << "ooo triangles: " << total << std::endl;

        // RRR - this means that a given line is dedicated to the runtime results
        // the columns are as follows:
        // RRR [Problem] [approximation-scheme] [baseline (problem + approx-scheme)] [graph-name] [thread count] [number of vertices] [number of edges] [treshold (BF parameter)] [b (another BF parameter-number of hash functions] [preprocessing-time] [tc-time] [total-runtime] [approximated TC count]

        std::cout << "RRR TC BF TC_BF " << graphName << " " << threads << " " << g.num_nodes() << " " << g.num_edges() << " " << tres << " " << k_temp << " " << m_temp << " " << pp_time << " " << tc_time << " " << pp_time + tc_time <<  " " << total << std::endl;

        // SSS - this means that a given line is dedicated to the size results
        // the columns are as follows:
        // SSS [Problem] [approximation-scheme] [baseline (problem + approx-scheme)] [graph-name] [thread count] [number of vertices] [number of edges] [treshold (BF parameter)] [b (another BF parameter-number of hash functions] [size of BF structures] [size of the original standard CSR (total)] [total size of both] [approximated TC count]

        std::cout << "SSS TC BF TC_BF " << graphName << " " << threads << " " << g.num_nodes() << " " << g.num_edges() << " " << tres << " " << k_temp << " " << m_temp << " " << approx_str_size << " " << initial_csr_size << " " << approx_str_size + initial_csr_size << " " << total << std::endl;

        printf("ooo -------------------------------\n");
    }
    free(thresholds);
    // return total;
    return 0;
}

void PrintTriangleStats(const Graph &g, size_t total_triangles) {
    cout << total_triangles << " triangles" << endl;
}


bool TCVerifier_null(const Graph &g, size_t approx_total, const CLApp &cli) {
    return true;
}



// Compares with simple serial implementation that uses std::set_intersection
bool TCVerifier(const Graph &g, size_t approx_total, const CLApp &cli) {
    size_t exact_total = 0;
    #pragma omp parallel for reduction(+ : exact_total) schedule(dynamic, 64)
    for (NodeID u=0; u < g.num_nodes(); u++) {
        for (NodeID v : g.out_neigh(u)) {
            if (v > u)
                break;
            auto it = g.out_neigh(u).begin();
            for (NodeID w : g.out_neigh(v)) {
                if (w > v)
                    break;
                while (*it < w)
                    it++;
                if (w == *it)
                    exact_total++;
            }
        }
    }
    cout << "accuracy: " << (float)((float)approx_total-exact_total)/exact_total*100 << "\%" << endl;
    cout << "approx total: " << approx_total << endl;
    cout << "exact total: " << exact_total << endl;
    if (exact_total != approx_total)
        cout << exact_total << " != " << approx_total << endl;
    return exact_total == approx_total;
}



int main(int argc, char* argv[]) {
    CLSIMDApp cli(argc, argv, "triangle count");
    if (!cli.ParseArgs())
        return -1;
    // cli.set_verify();
    Builder b(cli);
    Graph g = b.MakeGraph();
    if (g.directed()) {
        cout << "Input graph is directed but tc requires undirected" << endl;
        return -2;
    }
    auto ct = [&cli] (const Graph& g) {
        return OrderedCount(g, cli.treshold(), cli.k(), cli.m(), cli.get_parameters_file(), cli.getGraphBasename(), cli.getThreadNum());
    };
    BenchmarkKernel(cli, g, ct, PrintTriangleStats, TCVerifier_null);
    return 0;
}

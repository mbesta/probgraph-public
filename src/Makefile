# See LICENSE.txt for license details.

CXX=g++
#CXX=g++-8
# CXX_FLAGS += -std=c++11 -Wall -mavx2 -g -lmetis -lboost_system -Isrc/lib/ -Lsrc/lib/
#CXX_FLAGS += -std=c++11 -Wall -mavx2 -g  -I/home/saleh/Research/graph-sets/sketchgraph/boost_1_66_0 -Isrc/lib/ -Lsrc/lib/
CXX_FLAGS += -std=c++11 -Wall -march=native -g -Isrc/lib/ -Lsrc/lib/ -I boost_1_76_0


#CXX_FLAGS += -std=c++11 -Wall -mavx2 -g -Isrc/lib/ -Lsrc/lib/
PAR_FLAG = -fopenmp
OPT_FLAG = -O3
DEBUG_FLAG = -fkeep-inline-functions

ifneq (,$(findstring icpc,$(CXX)))
	PAR_FLAG = -openmp
endif

ifneq (,$(findstring sunCC,$(CXX)))
	CXX_FLAGS = -std=c++11 -xO3 -m64 -xtarget=native
	PAR_FLAG = -xopenmp
endif
ifneq ($(DEBUG),1)
	CXX_FLAGS += $(OPT_FLAG)
else
	CXX_FLAGS += $(DEBUG_FLAG) 
endif

ifneq ($(SERIAL), 1)
	CXX_FLAGS += $(PAR_FLAG)
endif

# KERNELS = tc_bloom_naive tc_minhash tc_minhash_block tc_bloom_block tc_bloom tc testSet
#KERNELS = tc_bloom_naive tc_minhash tc_minhash_block tc_bloom_block tc_bloom tc_bloom_myquery bloom_mc bloom_block_tc tc libbloom_tc testSet.cc # bc bfs cc cc_afforest pr sssp tc
#
#KERNELS = tc tc_doulion tc_colorful tc_variable tc_bloom tc_bloom_block link_prediction_bloom tc_bloom_naive tc_kmv tc_kmv_block tc_minhash tc_minhash_block nclique_brute nclique_kmv nclique_kmv_v2 nclique_minhash nclique_minhash_v2 nclique_std nclique_std_v2 clustering_bloom clustering_kmv clustering_minhash  testSet #for testing all algorithms
KERNELS = tc_doulion tc_colorful tc_bf tc_kh tc_1h tc_kmv tc_base jp-cn_bf jp-cn_kh jp-cn_1h jp-cn_kmv jp-cn_base jp-jc_bf jp-jc_kh jp-jc_1h jp-jc_kmv jp-jc_base jp-ov_bf jp-ov_kh jp-ov_1h jp-ov_kmv jp-ov_base 4c_bf 4c_bf 4c_1h 4c_kh 4c_kmv 4c_base

SUITE = $(KERNELS)

.PHONY: all
all: $(SUITE)

tc_set_simd: src/tc_set_simd.cc src/*.h src/*.hpp
	$(CXX) $(CXX_FLAGS) $< src/set_operation.cpp src/util.cpp -o $@

% : src/algorithms/%.cc src/*.h src/*.hpp
	$(CXX) $(CXX_FLAGS) $< src/set_operation.cpp src/sets.hpp src/util.cpp src/MurmurHash3.cpp -o $@

# g
# include test/test.mk

# Benchmark Automation
#include benchmark/bench.mk


.PHONY: clean
clean:
	rm -f $(SUITE) test/out/*

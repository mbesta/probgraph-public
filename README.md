
### Prerequirisites: #

  * boost 1.76
  * g++ 8.3.0
  * python 3.7

### How to execute: #

Run the following commands from the main probgraph-public folder:
```
cd src
make
cd ../ 
```

Now tun the test to check that everything works:

`./test.sh`

or you can try it yourself by running any of the executables in probgraph-public/src/
the general formulation is

`./src/PROBLEM_APPROXIMATOR OPTIONS`

possible choices for PROBLEM are:
  * `tc` : Triangle Counting
  * `jp-jc` : Clustering (Jaccard)
  * `jp-ov` : Clustering (Overlap)
  * `jp-cn` : Clustering (Common neigh.)
  * `4c`: 4-cliques

possible choices for APPROXIMATOR are:
  * `base` : Baseline
  * `1h`: one-hash
  * `bf`: Bloom Filter
  * `colorful`, `doulion` : only available for Triangle Counting

For example, 

`./src/tc_bf -g 17 -k 256`

will run Triangle counting (TC) using Bloom Filters (BF) on a Kronecker graph with 2^17 nodes and 256 avg. degree (-g 17 -k 256).
Run any executable with the -h flag to see the available options

To reproduce the experiments in the paper, run 

`./launch_all_experiments` (use the _CLUSTER version if you are on a cluster) 

Then, collect all results using 

`./collect_results.sh`

this will overwrite the existing csv files in the result folders. If you just want to generate the images from the existing data, skip the two previous steps and just run

`./generate_images.sh`

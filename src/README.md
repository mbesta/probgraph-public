## Source files
The relevant source files are all located in src/src/ including the set representation library ´sets.hpp´ and the
corresponding set based algorithms. All algorithms are adapted from the GAP implementation of triangle counting ´tc.cc´
 - src/tc\_bloom.cc´
 - src/tc\_minhash.cc´
 - src/nclique\_brute.cc´
 - src/nclique\_std_v2.cc´
 - src/nclique\_minhash_v2.cc´

## Compilation
The makefile was extended from the GAP project. To make one of the algorithms run e.g. ´$ make tc\_bloom´ so its source
file name without ".cc".
For the nclique algorithms, add "-DCOUNT" flag to enable counting instrumentation.

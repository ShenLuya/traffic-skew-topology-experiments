# Mesh and Torus main runs

This folder archives 140 run logs: two topologies, two traffic patterns, seven
offered rates, and five seeds.

The historical logs embed the complete BookSim configuration at their start.
The four files in `configs/` were recovered from those headers. The varying
offered rate and seed were supplied as command-line overrides, which are listed
for every run in `run_manifest.csv`.

`run_from_manifest.sh` defaults to a single smoke run and writes only to a new
`rerun_logs/` directory. It never overwrites `logs/`. Because the historical
upstream BookSim commit and build environment are unknown, new executions are
environment-sensitive replications; the archived logs remain the evidence for
the manuscript values.

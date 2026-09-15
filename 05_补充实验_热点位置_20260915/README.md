# Hotspot position pilot experiment

This preliminary experiment extends the completed 64-endpoint BookSim study.

- Topologies: Mesh, Torus, Fat-Tree
- Traffic: `hotspot_mix({node,20})`
- New hotspot nodes: 3 (edge) and 27 (interior)
- Injection rates: 0.06, 0.075, 0.08 flits/node/cycle
- Preliminary seeds: 101, 202, 303
- Existing node-0 results remain unchanged and are used as the Mesh corner baseline.

The pilot is intended to support manuscript drafting. Before final submission, extend each condition to seeds 404 and 505 and archive the exact `hotspot_mix` source patch used to build BookSim.

## Run status (2026-09-15)

- Completed: 54/54 runs
- Stable: 45 runs
- Congestion-threshold exits: 9 runs
- Failed: 0 runs
- BookSim endpoint count: 64 for all three topologies

Before the pilot, the executable was checked against the archived node-0 Mesh case
at rate 0.02 and seed 101. It reproduced packet latency 28.3384 cycles and accepted
rate 0.0193646 exactly.

The recovered `hotspot_mix({node,20})` implementation sends 20% of generated
destinations to the selected hotspot and distributes the other 80% uniformly over
the remaining 63 destinations.

BookSim executable SHA-256:
`FA038B961C3AD40500C81B102B6E5BF79E6E3CDF16AF3D658B4774A3CA1585E2`

The exact `traffic.cpp` and `traffic.hpp` used for `hotspot_mix` are archived in
`booksim_hotspot_mix_source/` in the D-drive/GitHub experiment package.

The comparison uses node-0 seeds 101, 202, and 303 so that all means use the same
three seeds. See `PRELIMINARY_RESULTS.md` for paper-writing conclusions and
`summary.csv` / `comparison_with_node0.csv` for the numeric results.

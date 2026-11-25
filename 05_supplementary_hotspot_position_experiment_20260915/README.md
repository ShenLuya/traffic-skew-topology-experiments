# Hotspot position pilot experiment

This preliminary experiment extends the completed 64-endpoint BookSim study.

- Topologies: Mesh, Torus, Fat-Tree
- Traffic: `hotspot_mix({node,20})`
- New hotspot nodes: 3 (edge) and 27 (interior)
- Injection rates: 0.06, 0.075, 0.08 flits/node/cycle
- Exploratory matched seeds: 101, 202, 303
- Existing node-0 results remain unchanged and are used as the Mesh corner baseline.

The three-seed design is intentional. This is an exploratory position-sensitivity
pilot, not a second confirmatory five-seed experiment. The manuscript labels it
accordingly and does not generalize beyond the tested positions and rates.

Nodes 0, 3, and 27 represent three positional classes in the 8 x 8 Mesh: a
corner, a non-corner boundary node, and an interior node. The same terminal
labels are retained in Torus and Fat-Tree for a matched exploratory comparison;
they do not imply that those topologies have identical geometric roles.

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

For a new rerun, set `BOOKSIM_BIN` explicitly. The runner writes to
`rerun_output/` by default and does not overwrite the archived `configs/` or
`logs/` folders:

```bash
BOOKSIM_BIN=/absolute/path/to/booksim bash run_hotspot_position_pilot.sh smoke
```

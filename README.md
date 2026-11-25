# Traffic-skew topology experiments

This repository archives the BookSim data and analysis used for the manuscript
*Impact of Traffic Skew on Network Topology Performance* (working title). The
paper's matched comparison covers three 64-endpoint configurations: an 8 x 8
Mesh, an 8 x 8 Torus, and a 64-terminal Fat-Tree.

The repository has two purposes:

1. preserve the run-level evidence behind the reported numbers; and
2. provide one documented, portable route for checking the archive and
   regenerating the paper figures without rerunning BookSim.

## Reproduce the paper figures

Python 3.10 or newer is recommended.

```bash
python -m pip install -r requirements.txt
python paper_reproduction/verify_archive.py
python paper_reproduction/redraw_figures.py
python "06_sensitivity_experiments/hotspot_percentage_sensitivity_completed_20261125/01_results/collect_results.py"
python "06_sensitivity_experiments/hotspot_percentage_sensitivity_completed_20261125/01_results/plot_results.py"
```

The main-archive verification command is read-only. The drawing commands
recompute tables and figures from archived run-level records; they do not run
a simulation or alter the archived logs.

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the evidence chain, status
definitions, exact study design, and limitations.

## Study design used by the manuscript

The matched main experiment contains 210 attempted runs:

```text
3 topologies x 2 traffic patterns x 7 offered rates x 5 seeds = 210 runs
```

- Topologies: Mesh, Torus, Fat-Tree (64 endpoints each)
- Traffic: uniform and `hotspot_mix({0,20})`
- Offered rates: 0.02, 0.04, 0.06, 0.07, 0.075, 0.08, and 0.10
  flits/node/cycle
- Seeds: 101, 202, 303, 404, and 505
- Routing: `dor` (Mesh), `min_adapt` (Torus), and `nca` (Fat-Tree)

The exploratory hotspot-position pilot contains 54 additional runs:

```text
3 topologies x 2 new hotspot nodes x 3 rates x 3 seeds = 54 runs
```

It deliberately uses three matched seeds (101, 202, and 303). Node 0 values
are drawn from the matching three seeds in the main archive; nodes 3 and 27
are the 54 new pilot runs. The pilot is reported as exploratory, not as another
five-seed confirmatory comparison.

The supplementary hotspot-share sensitivity experiment contains 180 runs:

```text
3 topologies x 4 hotspot shares x 3 offered rates x 5 seeds = 180 runs
```

It varies the node-0 hotspot share over 10%, 20%, 30%, and 40% at offered
rates 0.02, 0.03, and 0.04. Thirty overlapping 20% runs reproduce the archived
main-experiment outputs exactly. All 165 runs below the analytical destination
service bound reach converged stops; only the 40%-at-0.04 condition exceeds the
bound and is reported as an overloaded stress condition.

## Repository map

| Path | Role |
|---|---|
| `paper_reproduction/` | Canonical paper-facing data, verifier, figure script, and generated figures |
| `01_final_summary/` | Historical consolidated CSV/Excel results and earlier inspection plots |
| `02_booksim_main_experiments/01_mesh_torus_64_endpoints_5_seeds/` | Mesh/Torus logs, four base configurations, and 140-run manifest |
| `02_booksim_main_experiments/02_fat_tree_64_endpoints_5_seeds/` | Fat-Tree configurations and logs; the paper uses the 70 runs at its seven matched rates |
| `02_booksim_main_experiments/03_dragonfly_72_endpoints_5_seeds/` | Unequal-size supplementary work, not part of the manuscript's matched three-topology comparison |
| `05_supplementary_hotspot_position_experiment_20260915/` | Three-seed hotspot-position pilot and archived `hotspot_mix` source files |
| `03_gem5_audit_experiments_not_for_main_comparison/` | Legacy system-level audit data; explicitly excluded from the paper comparison |
| `05_run_and_summary_scripts/` | Historical collection/plotting scripts; read its README before use |
| `06_sensitivity_experiments/hotspot_percentage_sensitivity_completed_20261125/` | Completed 180-run hotspot-share sweep, raw logs, configurations, analysis scripts, figure, and isolated BookSim2 environment |

## What is and is not verified

The included verifiers check run counts, factorial designs, seed coverage,
CSV-to-log status and final-metric agreement, paper-data copies, and published
SHA-256 manifests. The archived main, position-pilot, and hotspot-share logs are
the evidence for the paper-facing CSV files. The sensitivity package also
retains the 30-run historical comparison used to verify exact overlap with the
20% main experiment.

The original BookSim executable used for the position pilot has SHA-256:

```text
FA038B961C3AD40500C81B102B6E5BF79E6E3CDF16AF3D658B4774A3CA1585E2
```

The exact modified `traffic.cpp` and `traffic.hpp` implementing
`hotspot_mix` are archived in
`05_supplementary_hotspot_position_experiment_20260915/booksim_hotspot_mix_source/`. The upstream
BookSim Git commit used to build the historical executable was not preserved,
so a source-level rebuild cannot honestly be claimed to be bit-for-bit
reproducible. This limitation is recorded rather than replaced by an invented
version identifier.

The completed hotspot-share sweep uses BookSim2 Git commit
`28f43299f1706a3160ffac721ca461d74eb6e618` with the archived `hotspot_mix`
source. Its verified BookSim binary has SHA-256:

```text
F5E8B8B6E2E87EF9794558158464D292B58FD1EEE14CD207AA9DCC7A1C59700A
```

The source tree, binary, compiler version, complete configurations, logs, and
exit-code sidecars are retained inside the sensitivity package.

## Legacy data boundary

The Dragonfly and gem5 folders are retained for audit history. They are not
combined with the 64-endpoint BookSim comparison. In particular,
`05_run_and_summary_scripts/generate_main_figures.py` is a retired script that mixed
BookSim and gem5 results and must not be used for the manuscript.

## Citation and license

Citation metadata are provided in `CITATION.cff`. No software/data license has
yet been selected by the author; see `LICENSE_SELECTION_REQUIRED.md`. Until a
license is added, copyright is retained and reuse permission is not implied.

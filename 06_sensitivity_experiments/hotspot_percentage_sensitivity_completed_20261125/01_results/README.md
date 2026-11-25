# Hotspot-percentage sensitivity experiment

This directory contains the new BookSim2 sensitivity experiment requested on
2026-11-25. It extends the archived 20% single-hotspot setup without changing
the topology, routing, flow-control, packet, seed, or stopping settings.

## Design

- Topology--routing configurations: Mesh--`dor`, Torus--`min_adapt`, and
  Fat-Tree--`nca`
- Endpoints: 64 (`k=8`, `n=2`)
- Hotspot destination: node 0
- Hotspot percentages: 10%, 20%, 30%, and 40%
- Offered rates: 0.02, 0.03, and 0.04 flits/node/cycle
- Seeds: 101, 202, 303, 404, and 505
- Total: 4 x 3 x 3 x 5 = 180 runs
- Flow control: 16 VCs and 16 flits of buffer per VC
- Packet size: one flit
- Stopping protocol: BookSim latency mode, three warmup periods, 1,000-cycle
  sampling periods, and the historical default limit of ten sampling periods

## Execution rule

The BookSim2 build is an isolated copy of Git commit
`28f43299f1706a3160ffac721ca461d74eb6e618` with the exact archived
`hotspot_mix` `traffic.cpp` and `traffic.hpp`. Before the full batch, the smoke
test must reproduce the historical Mesh, 20%, 0.02, seed-101 result exactly:

- packet latency: 28.3384 cycles
- injected flit rate: 0.0194062
- accepted flit rate: 0.0193646

Archived paper data are not overwritten. New configs, logs, exit-code sidecars,
the manifest, and provenance records remain in this directory.

## Verified outputs

The completed batch contains 167 converged stops, 10 maximum-sample stops,
and 3 threshold exits. All 30 runs that overlap the historical 20% dataset
match exactly. See `experiment_report.md` for the audited interpretation,
`summary.csv` for the 36 aggregated cells, and `figures/` for the paper-ready
PDF and PNG figure.

The two archived input tables used for the 30-run exact reproducibility check
are retained under `historical_reference/`, so `collect_results.py` remains
self-contained after the experiment bundle is moved.

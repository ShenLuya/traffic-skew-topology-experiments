# Hotspot-Percentage Sensitivity Experiment Report

## 1. Executive summary

All 180 BookSim2 executions were run and parsed, covering 36 complete experiment cells. Thirty runs overlap the historical 20% hotspot configurations at injection rates 0.02 and 0.04. Their run-level metrics reproduce the historical records exactly (30/30), supporting consistency between the recovered `hotspot_mix` implementation, the new configurations, and the earlier experiment method.

Across the 33 cells whose analytical destination load remains below 1 flit/cycle, all 165 runs reached BookSim converged stops. The only condition above the necessary destination-service bound is `40% hotspot x 0.04 injection rate`:

\[
64 \times 0.40 \times 0.04 = 1.024\ \text{flits/cycle}.
\]

All three topology-routing configurations degrade under this condition, but their run outcomes differ. Mesh-`dor` and Fat-Tree-`nca` each have four of five maximum-sample stops. Torus-`min_adapt` has two of five maximum-sample stops and three of five 500-cycle threshold exits. These 13 runs must not be described as all converged, and the Torus threshold exits have no final latency value.

## 2. Experiment provenance

- Simulator: BookSim2, Git commit `28f43299f1706a3160ffac721ca461d74eb6e618`
- BookSim binary SHA-256: `f5e8b8b6e2e87ef9794558158464d292b58fd1eee14cd207aa9dcc7a1c59700a`
- `traffic.cpp` SHA-256: `874207df0277ad9e12bc2651d2c62c3e2b2994c82378158a10d9e463cf456900`
- `traffic.hpp` SHA-256: `a677db0789a8e201343b8b9f22874f56609f084ed0a9c98c6fbafe3d8e170261`
- Compiler: g++ 14.2.0
- Network size: 64 endpoints; Mesh and Torus use `k=8, n=2`
- Configurations: Mesh-`dor`, Torus-`min_adapt`, and Fat-Tree-`nca`
- Flow control: 16 VCs with a 16-flit buffer per VC
- Allocators: `islip` VC and switch allocators, `alloc_iters=2`
- Packet size: 1 flit
- Traffic: `hotspot_mix({0,p})`; node 0 is the hotspot and remaining traffic is distributed uniformly among the other 63 nodes
- Hotspot shares: 10%, 20%, 30%, and 40%
- Injection rates: 0.02, 0.03, and 0.04 flits/node/cycle
- Seeds: 101, 202, 303, 404, and 505
- Stop protocol: latency mode; 3 warmup periods; 1,000-cycle sample period; at most 10 sample phases; 500-cycle latency threshold
- Total executions: `4 x 3 x 3 x 5 = 180`
- Per-run external timeout: 180 s; no external timeout or runner crash occurred
- Execution window: 2026-11-25 21:28:34-21:30:29 local time (approximately 115 s wall time)

## 3. Run-outcome audit

| Outcome | Mesh | Torus | Fat-Tree | Total |
|---|---:|---:|---:|---:|
| converged stop | 56 | 55 | 56 | 167 |
| maximum-sample stop | 4 | 2 | 4 | 10 |
| threshold exit | 0 | 3 | 0 | 3 |
| total | 60 | 60 | 60 | 180 |

In this BookSim2 build, `TrafficManager::Run()` success causes `main` to return `-1`, which appears as process exit code 255 in the Linux sidecar. The 177 code-255 records are therefore not program crashes. The three code-0 records correspond to explicit `Simulation unstable, ending ...` threshold exits.

## 4. Mean packet latency (cycles)

Values normally summarize five seeds. An asterisk marks a cell containing maximum-sample stops and therefore not a strictly established steady-state mean. The dagger marks the Torus cell in which only two maximum-sample runs have final statistics and the other three runs are threshold exits.

| Configuration | Injection rate | 10% | 20% | 30% | 40% |
|---|---:|---:|---:|---:|---:|
| Mesh-`dor` | 0.02 | 27.55 | 28.43 | 29.10 | 29.79 |
| Mesh-`dor` | 0.03 | 27.56 | 28.36 | 29.25 | 30.55 |
| Mesh-`dor` | 0.04 | 27.65 | 28.46 | 29.72 | 90.65* |
| Torus-`min_adapt` | 0.02 | 26.14 | 26.10 | 26.19 | 26.31 |
| Torus-`min_adapt` | 0.03 | 26.12 | 26.20 | 26.50 | 27.46 |
| Torus-`min_adapt` | 0.04 | 26.12 | 26.38 | 27.14 | 174.54† |
| Fat-Tree-`nca` | 0.02 | 13.08 | 13.04 | 13.12 | 13.22 |
| Fat-Tree-`nca` | 0.03 | 13.07 | 13.12 | 13.23 | 13.83 |
| Fat-Tree-`nca` | 0.04 | 13.05 | 13.16 | 13.58 | 117.54* |

The 95% Student-t intervals and per-cell outcome counts are retained in `summary.csv`.

## 5. Interpretation boundary

The analytical relation identifies a necessary shared-destination capacity boundary: when `64 x p x lambda > 1`, the offered load to the hotspot exceeds its one-flit-per-cycle ejection capacity. It does not predict the exact latency of a topology-routing configuration, which configuration degrades first, seed variability, whether BookSim's convergence criterion is met, or routing-induced internal congestion. The experiment adds those empirical observations.

The `40% x 0.04` cell should be described as an analytically overloaded stress condition. Open diamonds in the figure are finite-run estimates. The three Torus threshold exits have no final latency statistics. The values 90.65, 174.54, and 117.54 cycles must not be ranked as established steady-state performance.

## 6. Artifacts

- `raw_runs.csv`: 180 run-level records, outcomes, rates, and relative paths
- `summary.csv`: 36 cells, 95% Student-t intervals, and destination-bound information
- `historical_20pct_comparison.csv`: 30 historical-overlap checks
- `verification_report.txt`: automated verification summary
- `figures/hotspot_percentage_latency.pdf`: manuscript vector figure
- `figures/hotspot_percentage_latency.png`: 300-dpi preview
- `configs/` and `logs/`: all configurations, raw logs, and exit-code sidecars
- `provenance_all.txt`: execution provenance

Historical data and manuscript files were not overwritten.

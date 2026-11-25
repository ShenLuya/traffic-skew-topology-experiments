# Hotspot-Percentage Sensitivity Experiment (Completed 2026-11-25)

This directory is the canonical package for the completed sensitivity and reproducibility batch. Historical experiments and manuscript files were not overwritten.

## Start with these files

- `01_results/experiment_report.md`: complete design, status audit, numerical summary, and interpretation boundaries.
- `01_results/SENSITIVITY_ANALYSIS_INTERPRETATION.md`: how the batch relates to the 20% main experiment and which claims the data do and do not support.
- `01_results/figures/hotspot_percentage_latency.pdf`: vector figure used by the manuscript.
- `01_results/figures/hotspot_percentage_latency.png`: raster preview.
- `01_results/summary.csv`: 36 topology-share-rate cells.
- `01_results/raw_runs.csv`: all 180 run-level records.
- `01_results/configs/` and `01_results/logs/`: all configurations, original logs, and exit-code sidecars.
- `02_booksim2_reproduction_environment/`: source snapshot and verified BookSim2 binary used for this batch.
- `FILE_MANIFEST_SHA256.csv`: file-level size and SHA-256 manifest for this package.

## Result in one paragraph

All 165 runs whose analytical destination load remained below 1 flit/cycle reached BookSim converged stops. The only overloaded cell was 40% hotspot share at an injection rate of 0.04, for which the offered destination load was 1.024 flits/cycle. All three tested topology-routing configurations degraded in that cell, but their run outcomes differed. These observations are reported as overloaded finite-run or threshold-exit outcomes, not as comparable steady-state latency rankings.

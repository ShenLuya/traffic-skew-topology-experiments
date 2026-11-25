# Directory Guide

This package contains the complete 180-run hotspot-percentage sensitivity and reproducibility batch.

- `01_results/`: configurations, original logs, exit-code sidecars, run-level and summary CSVs, verification records, figures, and the analysis/plotting programs.
- `02_booksim2_reproduction_environment/`: the isolated BookSim2 source snapshot and verified binary used for this batch. Nested Git metadata and intermediate object/dependency files are intentionally excluded.
- `FILE_MANIFEST_SHA256.csv`: byte size and SHA-256 for every other file in this package.

The package is self-contained for auditing this batch. It does not overwrite or replace the historical main-experiment archive.

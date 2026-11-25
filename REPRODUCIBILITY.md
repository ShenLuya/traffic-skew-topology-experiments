# Reproducibility guide

## Scope

This guide distinguishes three different activities that are often conflated:

1. **Archive verification** checks that the CSV records agree with the archived
   logs and with the documented experimental design.
2. **Figure regeneration** recomputes manuscript summaries from run-level CSVs,
   redraws the four main/pilot figures, and redraws the supplementary
   hotspot-share figure.
3. **Simulation rerun** executes BookSim again. This requires a compatible
   BookSim build and is not needed to audit the submitted numerical claims.

## 1. Verify the archive

From the repository root:

```bash
python paper_reproduction/verify_archive.py
python "06_sensitivity_experiments/hotspot_percentage_sensitivity_completed_20261125/01_results/collect_results.py"
```

The main verifier is read-only. The sensitivity collector reparses archived
logs and rewrites its derived CSV/report files deterministically. Together they
check:

- exactly 210 matched main attempts;
- five-seed coverage for every topology/traffic/rate cell;
- 140 Mesh/Torus and 70 paper-rate Fat-Tree attempts;
- exactly 54 new pilot attempts and three-seed coverage;
- completed versus threshold-exit agreement between CSV files and logs;
- final latency, injected-rate, and accepted-rate agreement where a run
  completed;
- byte identity between the paper-facing CSV copies and their archive sources;
- the SHA-256 entries in `SHA256SUMS-paper.txt`.
- exactly 180 hotspot-share executions with five-seed coverage across 36 cells;
- 30/30 exact matches for conditions overlapping the historical 20% archive;
- 167 converged stops, 10 maximum-sample stops, and 3 threshold exits.

Success ends with `VERIFIED`. A failed check exits non-zero and names the file
or condition that needs attention.

## 2. Regenerate figures and derived tables

Install the two plotting dependencies and run:

```bash
python -m pip install -r requirements.txt
python paper_reproduction/redraw_figures.py
python "06_sensitivity_experiments/hotspot_percentage_sensitivity_completed_20261125/01_results/plot_results.py"
```

Outputs are written under `paper_reproduction/generated/`:

- `recomputed_main_summary.csv`
- `recomputed_ldf.csv`
- `recomputed_position_summary.csv`
- `figures/main_latency.{pdf,png}`
- `figures/rate_ratio.{pdf,png}`
- `figures/main_ldf.{pdf,png}`
- `figures/position_pilot.{pdf,png}`

The sensitivity script writes its reference manuscript figure to:

- `06_sensitivity_experiments/hotspot_percentage_sensitivity_completed_20261125/01_results/figures/hotspot_percentage_latency.{pdf,png}`

The tracked files in `paper_reproduction/figures/` are the reference outputs
used by the current manuscript. They are not overwritten by default.

### Statistical conventions

- A run is completed when its status is `OK` or `STABLE`.
- A failed latency-stability condition is retained as a threshold exit, not
  converted into a latency observation.
- Main means and 95% intervals use the five predefined seeds when all five
  completed. The interval is a two-sided Student-t interval with 4 degrees of
  freedom.
- The position pilot uses three matched seeds and a Student-t interval with 2
  degrees of freedom. It is explicitly exploratory.
- LDF is the ratio of the five-seed hotspot mean latency to the five-seed
  uniform mean latency at the same topology and offered rate. No confidence
  interval for this ratio is claimed.
- Accepted/injected is a finite-window rate ratio. It is not interpreted as a
  packet-loss probability or as an independent stability test.
- Sensitivity cells containing maximum-sample stops are finite-run estimates.
  Threshold exits are status markers and are not assigned a latency value.

## 3. Rerun the simulations

### Historical BookSim dependency

The experiments used a modified BookSim 2 build. The `hotspot_mix` source files
are archived, and the pilot executable hash is recorded, but the upstream Git
commit was not preserved. Therefore:

- archive verification and figure regeneration are fully available here;
- an exact historical binary rebuild cannot be guaranteed;
- reruns with a newly built BookSim should be treated as environment-sensitive
  replication, not as proof of byte-for-byte identity.

The upstream project is commonly obtained from
<https://github.com/booksim/booksim2>. Replace its traffic implementation only
after reviewing the archived source differences. Do not assume that an
arbitrary upstream revision is identical to the historical base.

### Mesh and Torus

Four recovered base configurations are in:

```text
02_booksim_main_experiments/01_mesh_torus_64_endpoints_5_seeds/configs/
```

`run_manifest.csv` lists all 140 historical topology/traffic/rate/seed
combinations and the corresponding archived log. Each row gives the base
configuration plus the two runtime overrides used historically:

```bash
booksim BASE_CONFIG injection_rate=RATE seed=SEED
```

Set `BOOKSIM_BIN` and use the supplied runner only when a rerun is intended:

```bash
BOOKSIM_BIN=/absolute/path/to/booksim \
  bash 02_booksim_main_experiments/01_mesh_torus_64_endpoints_5_seeds/run_from_manifest.sh smoke
```

The default `smoke` mode writes to a new `rerun_logs/` directory. The script
does not overwrite the archived logs. Read and compare the smoke output before
running `all`.

### Fat-Tree and position pilot

Fat-Tree already contains per-run configuration files. The position pilot also
contains its exact configurations and a portable runner. The manuscript's
matched main comparison excludes Fat-Tree rate 0.01, Dragonfly, and all gem5
results.

### Hotspot-share sensitivity sweep

The completed sensitivity package is self-contained under:

```text
06_sensitivity_experiments/hotspot_percentage_sensitivity_completed_20261125/
```

It retains the BookSim2 source tree at Git commit
`28f43299f1706a3160ffac721ca461d74eb6e618`, the modified `hotspot_mix`
implementation, the verified binary, compiler provenance, all 180
configurations and logs, and the batch runner. Its 30 runs overlapping
the historical 20% archive match exactly at the seed and metric level. Read
`README_FIRST.md` and `01_results/experiment_report.md` before rerunning; the
archived results should not be overwritten.

## Provenance boundaries and known limitations

- The main Mesh/Torus CSV historically contained obsolete `log_file` prefixes.
  The paper-facing copy uses repository-relative paths; numerical columns are
  unchanged.
- Mesh/Torus logs embed the full configuration at their beginning. The four
  base configuration files were recovered verbatim from these log headers.
- The original build command, compiler version, operating-system image, and
  upstream BookSim commit were not archived for the historical main and
  position-pilot executables. These are material limitations for an exact
  historical source rebuild; they do not apply to the separately archived
  2026-11-25 hotspot-share environment.
- The repository retains legacy Dragonfly and gem5 work for transparency, but
  those data are not evidence for the manuscript's matched comparison.

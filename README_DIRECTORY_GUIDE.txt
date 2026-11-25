Repository directory guide (updated 2026-11-25)

This submission-oriented copy was prepared from the original experiment archive without overwriting it. The manuscript's matched comparison covers three 64-endpoint topologies simulated in BookSim: Mesh, Torus, and Fat-Tree.

Start here:
1. README.md explains the study scope, 210 main runs, 54 hotspot-position pilot runs, and 180 hotspot-percentage sensitivity runs.
2. REPRODUCIBILITY.md explains data verification, figure regeneration, and the limits of the recovered historical environment.
3. paper_reproduction/ contains the paper-facing data, archive verifier, and figure-regeneration program.

Directory scope:
- 01_final_summary: historical consolidated tables and inspection artifacts.
- 02_booksim_main_experiments: BookSim main-experiment configurations and logs for the 64-endpoint Mesh, Torus, and Fat-Tree comparison. The 72-endpoint Dragonfly archive is retained separately and is not part of the matched comparison.
- 03_gem5_audit_experiments_not_for_main_comparison: retained for audit only; these results are not used in the matched main comparison.
- 04_code_modification_archive: historical simulator and traffic-model code snapshots.
- 05_supplementary_hotspot_position_experiment_20260915: the intentionally exploratory three-seed hotspot-position pilot.
- 05_run_and_summary_scripts: historical run and summary programs. Read its README before use; the retired mixed BookSim/gem5 plotting program is not part of the paper workflow.
- 06_sensitivity_experiments: the completed 180-run hotspot-percentage sensitivity and reproducibility batch, plus notes on optional out-of-scope follow-up work.
- paper_reproduction: canonical paper-facing data, verification code, and regenerated figures.

Important boundaries:
- The 210 main experiments are complete and do not need to be rerun merely because the repository was reorganized.
- The paper figures can be regenerated from archived run-level records with paper_reproduction/redraw_figures.py and the sensitivity plotting script documented in REPRODUCIBILITY.md.
- The archive verifier cross-checks run coverage, status classification, final metrics, and SHA-256 checksums.
- The hotspot-position pilot contains 54 runs: 3 configurations x 2 additional hotspot destinations x 3 offered rates x 3 seeds.
- The hotspot-percentage batch contains 180 runs: 4 hotspot shares x 3 offered rates x 3 configurations x 5 seeds.
- Dragonfly uses 72 endpoints, and the gem5 audit uses a different simulation setup; neither is included in the manuscript's matched three-configuration comparison.
- Historical hotspot-traffic source snapshots and executable hashes are retained, but the original upstream BookSim commit and complete historical build environment were not preserved. The repository therefore supports archive verification and figure regeneration, not a claim of bit-for-bit reconstruction of every historical simulator run.
- Raw logs are preserved as generated and may contain original local environment strings. They are evidence files, not reviewer-facing instructions.
- The author has not yet selected a repository license; see LICENSE_SELECTION_REQUIRED.md.

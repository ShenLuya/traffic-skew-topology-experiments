# Historical run and aggregation scripts

These files are retained for provenance. They are not the canonical route for
reproducing the current manuscript figures. Use:

```bash
python paper_reproduction/verify_archive.py
python paper_reproduction/redraw_figures.py
```

## Safety and status

- `generate_main_figures.py` is retired and exits immediately. It mixed
  BookSim and gem5 results measured under incompatible setups.
- `generate_final_booksim_figures.py` is a legacy plotter that includes the
  unequal-size 72-endpoint Dragonfly supplement. It is not used by the current
  three-topology manuscript.
- `collect_final_booksim_results.py` is a historical collector. It uses
  `BOOKSIM_ROOT` and optionally `BOOKSIM_RESULTS_OUTPUT`; its default output is
  a new `collected_results/` folder beside the script.
- `build_final_results_workbook.mjs` reads `BOOKSIM_RESULTS_DIR` or defaults to
  the repository's `01_final_summary/`. It depends on a nonstandard historical
  workbook package and is not required for verification.
- Shell scripts named with 20260812 reproduce historical batch layouts and may
  assume a Linux BookSim working tree. Review them before running. They are not
  called by the paper reproduction package.

The current paper-facing Python dependencies are listed only in the root
`requirements.txt`. No gem5 result is used in the paper figures.

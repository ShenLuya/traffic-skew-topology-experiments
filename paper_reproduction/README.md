# Paper reproduction package

This directory is the canonical, paper-facing subset of the repository.

## Contents

- `data/`: run-level inputs used by the current manuscript
- `figures/`: tracked reference PDF and PNG figures
- `redraw_figures.py`: read-only input processing and figure regeneration
- `verify_archive.py`: evidence-chain and checksum verification
- `generated/`: local outputs created by `redraw_figures.py` (not an input)

## Commands

From the repository root:

```bash
python paper_reproduction/verify_archive.py
python paper_reproduction/redraw_figures.py
```

The first command requires only the Python standard library. The second needs
the packages in the root `requirements.txt`.

## Input boundaries

`mesh_torus_raw_runs.csv` contributes 140 attempts. The paper selects 70
Fat-Tree attempts at the seven matched offered rates from
`fattree64_raw_runs.csv`; its additional ten rate-0.01 attempts remain archived
but are not used. `position_raw_runs.csv` contains the 54 new node-3/node-27
pilot attempts. The node-0 pilot baseline is selected from the first data file
using the matched seeds 101, 202, and 303.

No Dragonfly or gem5 data enter this package.

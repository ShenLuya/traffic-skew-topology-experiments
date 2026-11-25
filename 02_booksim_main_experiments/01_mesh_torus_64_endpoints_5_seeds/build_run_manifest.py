#!/usr/bin/env python3
"""Rebuild the deterministic 140-row Mesh/Torus run manifest."""

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
RATES = ("0.02", "0.04", "0.06", "0.07", "0.075", "0.08", "0.10")
SEEDS = (101, 202, 303, 404, 505)


def main() -> None:
    rows = []
    for topology in ("mesh", "torus"):
        for traffic in ("uniform", "hotspotmix"):
            config = f"configs/{topology}_{'uniform' if traffic == 'uniform' else 'hotspotmix_node0_20pct'}_base.conf"
            for rate in RATES:
                for seed in SEEDS:
                    log = f"logs/{topology}_{traffic}_rate{rate}_seed{seed}.txt"
                    if not (HERE / log).is_file():
                        raise SystemExit(f"missing archived log: {log}")
                    rows.append(
                        {
                            "topology": topology,
                            "traffic": traffic,
                            "injection_rate": rate,
                            "seed": seed,
                            "base_config": config,
                            "archived_log": log,
                        }
                    )
    output = HERE / "run_manifest.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Normalize obsolete Mesh/Torus log paths in the three archived CSV copies."""

import csv
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
TARGETS = (
    REPO / "01_最终汇总" / "mesh_torus_raw_runs.csv",
    REPO / "02_BookSim主实验" / "01_Mesh_Torus_64端点_5种子" / "raw_runs.csv",
    REPO / "paper_reproduction" / "data" / "mesh_torus_raw_runs.csv",
)
PREFIX = "02_BookSim主实验/01_Mesh_Torus_64端点_5种子/logs"


def normalize(path: Path) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames
    if not fields or "log_file" not in fields:
        raise SystemExit(f"missing log_file column: {path}")
    for row in rows:
        old_name = Path(row["log_file"].replace("\\", "/")).name
        row["log_file"] = f"{PREFIX}/{old_name}"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    counts = {path.relative_to(REPO).as_posix(): normalize(path) for path in TARGETS}
    if set(counts.values()) != {140}:
        raise SystemExit(f"unexpected row counts: {counts}")
    first = TARGETS[0].read_bytes()
    if any(path.read_bytes() != first for path in TARGETS[1:]):
        raise SystemExit("normalized copies differ")
    for path, count in counts.items():
        print(f"{path}: {count} rows")


if __name__ == "__main__":
    main()

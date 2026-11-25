#!/usr/bin/env python3
import csv
import math
import os
import shutil
from pathlib import Path

HOME = Path.home()
BOOKSIM = Path(os.environ.get("BOOKSIM_ROOT", HOME / "booksim2"))
OUTPUT = Path(os.environ.get("BOOKSIM_RESULTS_OUTPUT", Path(__file__).resolve().parent / "collected_results"))
OUTPUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "mesh_torus_summary.csv": BOOKSIM / "rerun_hotspot_mix/main_5seeds/summary.csv",
    "mesh_torus_raw_runs.csv": BOOKSIM / "rerun_hotspot_mix/main_5seeds/raw_runs.csv",
    "fattree64_summary.csv": BOOKSIM / "formal_fattree64_20260812/summary.csv",
    "fattree64_raw_runs.csv": BOOKSIM / "formal_fattree64_20260812/raw_runs.csv",
    "dragonfly72_summary.csv": BOOKSIM / "formal_dragonfly72_unitlat_20260812/summary.csv",
    "dragonfly72_raw_runs.csv": BOOKSIM / "formal_dragonfly72_unitlat_20260812/raw_runs.csv",
}

for output_name, source in SOURCES.items():
    if not source.exists():
        raise SystemExit(f"Missing source: {source}")
    shutil.copy2(source, OUTPUT / output_name)


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def clean_number(value):
    if value is None or value == "":
        return ""
    number = float(value)
    if not math.isfinite(number):
        return ""
    return number


COMMON_RATES = {0.02, 0.04, 0.06, 0.07, 0.075, 0.08, 0.10}
summary_rows = []
for filename in ("mesh_torus_summary.csv", "fattree64_summary.csv", "dragonfly72_summary.csv"):
    for row in read_csv(OUTPUT / filename):
        topology = row["topology"]
        endpoints = 72 if topology == "dragonfly72" else 64
        summary_rows.append({
            "topology": topology,
            "endpoints": endpoints,
            "traffic": row["traffic"],
            "injection_rate": clean_number(row["injection_rate"]),
            "total_runs": int(row["total_runs"]),
            "stable_runs": int(row["stable_runs"]),
            "unstable_runs": int(row["unstable_runs"]),
            "failed_runs": int(row.get("failed_runs", 0) or 0),
            "status": row["status"],
            "mean_latency_cycles": clean_number(row.get("mean_latency")),
            "std_latency_cycles": clean_number(row.get("std_latency")),
            "ci95_latency_cycles": clean_number(row.get("ci95_latency")),
            "mean_accepted_rate": clean_number(row.get("mean_accepted_rate")),
            "comparison_scope": "main_64_endpoint" if endpoints == 64 else "supplementary_72_endpoint",
        })

summary_rows.sort(key=lambda row: (row["comparison_scope"], row["topology"], row["traffic"], row["injection_rate"]))
summary_path = OUTPUT / "all_topologies_summary.csv"
with summary_path.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=summary_rows[0].keys())
    writer.writeheader()
    writer.writerows(summary_rows)

main_rows = [
    row for row in summary_rows
    if row["comparison_scope"] == "main_64_endpoint"
    and row["injection_rate"] in COMMON_RATES
]
main_path = OUTPUT / "main_64endpoint_summary.csv"
with main_path.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=main_rows[0].keys())
    writer.writeheader()
    writer.writerows(main_rows)

# Single-seed scan is used only to locate the Dragonfly hotspot saturation boundary.
scan_dir = BOOKSIM / "scan_dragonfly72_unitlat_20260812/logs"
scan_rows = []
for rate in (0.02, 0.04, 0.06, 0.08, 0.10):
    path = scan_dir / f"dragonfly72_hotspotmix_{rate:.2f}_seed101.txt"
    if not path.exists():
        continue
    text = path.read_text(errors="replace")
    status = "UNSTABLE" if "Simulation unstable" in text else "STABLE"
    scan_rows.append({
        "topology": "dragonfly72",
        "endpoints": 72,
        "traffic": "hotspotmix",
        "injection_rate": rate,
        "seed": 101,
        "status": status,
        "evidence_use": "boundary_scan_only_not_five_seed_mean",
    })

scan_path = OUTPUT / "dragonfly72_hotspot_boundary_scan.csv"
with scan_path.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=scan_rows[0].keys())
    writer.writeheader()
    writer.writerows(scan_rows)

expected_main = 3 * 2 * 7
expected_dragonfly = 7 + 2
if len(main_rows) != expected_main:
    raise SystemExit(f"Expected {expected_main} main summary rows, found {len(main_rows)}")
dragonfly_rows = [row for row in summary_rows if row["topology"] == "dragonfly72"]
if len(dragonfly_rows) != expected_dragonfly:
    raise SystemExit(f"Expected {expected_dragonfly} Dragonfly summary rows, found {len(dragonfly_rows)}")

print(f"output={OUTPUT}")
print(f"main_rows={len(main_rows)} dragonfly_rows={len(dragonfly_rows)} scan_rows={len(scan_rows)}")

#!/usr/bin/env python3
import csv
import math
import re
import statistics
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
LOG_DIR = BASE / "logs"
RAW_OUT = BASE / "raw_runs.csv"
SUMMARY_OUT = BASE / "summary.csv"
COMPARISON_OUT = BASE / "comparison_with_node0.csv"

NAME_RE = re.compile(
    r"^(mesh|torus|fattree)_hotspot_node(3|27)_rate(0\.06|0\.075|0\.08)_seed(101|202|303)\.txt$"
)
LAT_RE = re.compile(r"^Packet latency average = ([0-9.eE+-]+) \(1 samples\)$", re.M)
INJ_RE = re.compile(r"^Injected packet rate average = ([0-9.eE+-]+) \(1 samples\)$", re.M)
ACC_RE = re.compile(r"^Accepted packet rate average = ([0-9.eE+-]+) \(1 samples\)$", re.M)


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


rows = []
for path in sorted(LOG_DIR.glob("*.txt")):
    match = NAME_RE.match(path.name)
    if not match:
        continue
    topology, position, rate, seed = match.groups()
    text = path.read_text(errors="replace")
    unstable = "Simulation unstable" in text
    complete = "Total run time" in text
    latencies = LAT_RE.findall(text)
    injected = INJ_RE.findall(text)
    accepted = ACC_RE.findall(text)
    if unstable:
        status = "UNSTABLE"
    elif complete and latencies:
        status = "STABLE"
    else:
        status = "FAILED"
    rows.append(
        {
            "topology": topology,
            "hotspot_node": int(position),
            "injection_rate": float(rate),
            "seed": int(seed),
            "status": status,
            "latency_cycles": float(latencies[-1]) if status == "STABLE" else "",
            "injected_rate": float(injected[-1]) if status == "STABLE" and injected else "",
            "accepted_rate": float(accepted[-1]) if status == "STABLE" and accepted else "",
            "log_file": str(path.relative_to(BASE)),
        }
    )

write_csv(RAW_OUT, rows, list(rows[0].keys()) if rows else ["topology"])

groups = {}
for row in rows:
    key = (row["topology"], row["hotspot_node"], row["injection_rate"])
    groups.setdefault(key, []).append(row)

summary = []
for key, group in sorted(groups.items()):
    stable = [row for row in group if row["status"] == "STABLE"]
    values = [row["latency_cycles"] for row in stable]
    std = statistics.stdev(values) if len(values) > 1 else (0.0 if values else None)
    t_95 = 4.302652729911275 if len(values) == 3 else None
    ci95 = t_95 * std / math.sqrt(3) if t_95 is not None else None
    summary.append(
        {
            "topology": key[0],
            "hotspot_node": key[1],
            "injection_rate": key[2],
            "total_runs": len(group),
            "stable_runs": len(stable),
            "unstable_runs": sum(row["status"] == "UNSTABLE" for row in group),
            "failed_runs": sum(row["status"] == "FAILED" for row in group),
            "status": "STABLE" if len(stable) == len(group) else ("UNSTABLE" if not stable else "MIXED"),
            "mean_latency_cycles": statistics.mean(values) if values else "",
            "std_latency_cycles": std if std is not None else "",
            "ci95_latency_cycles": ci95 if ci95 is not None else "",
            "mean_accepted_rate": statistics.mean(row["accepted_rate"] for row in stable) if stable else "",
        }
    )

write_csv(SUMMARY_OUT, summary, list(summary[0].keys()) if summary else ["topology"])

if len(sys.argv) > 1:
    node0_path = Path(sys.argv[1])
    with node0_path.open(newline="", encoding="utf-8-sig") as handle:
        node0_rows = list(csv.DictReader(handle))
    node0 = {
        (row["topology"], float(row["injection_rate"])): row
        for row in node0_rows
        if row["traffic"] == "hotspotmix" and float(row["injection_rate"]) in {0.06, 0.075, 0.08}
    }
    if len(sys.argv) > 2:
        main_log_root = Path(sys.argv[2])
        node0_runs = {}
        main_name_res = (
            re.compile(r"^(mesh|torus)_hotspotmix_rate(0\.06|0\.075|0\.08)_seed(101|202|303)\.txt$"),
            re.compile(r"^fattree64_hotspotmix_(0\.06|0\.075|0\.08)_seed(101|202|303)\.txt$"),
        )
        for path in main_log_root.rglob("*.txt"):
            match = main_name_res[0].match(path.name)
            if match:
                topology, rate, _seed = match.groups()
            else:
                match = main_name_res[1].match(path.name)
                if not match:
                    continue
                rate, _seed = match.groups()
                topology = "fattree"
            text = path.read_text(errors="replace")
            values = LAT_RE.findall(text)
            key = (topology, float(rate))
            node0_runs.setdefault(key, []).append(
                None if "Simulation unstable" in text or not values else float(values[-1])
            )
        for key, values in node0_runs.items():
            stable_values = [value for value in values if value is not None]
            node0[key] = {
                "status": "STABLE" if len(stable_values) == len(values) else "UNSTABLE",
                "mean_latency_cycles": statistics.mean(stable_values) if stable_values else "",
            }
    comparison = []
    for row in summary:
        baseline = node0.get((row["topology"], row["injection_rate"]))
        comparison.append(
            {
                **row,
                "node0_status": baseline["status"] if baseline else "MISSING",
                "node0_mean_latency_cycles": baseline["mean_latency_cycles"] if baseline else "",
                "node0_seed_count": 3 if len(sys.argv) > 2 else 5,
                "latency_ratio_vs_node0": (
                    float(row["mean_latency_cycles"]) / float(baseline["mean_latency_cycles"])
                    if baseline and row["mean_latency_cycles"] and baseline["mean_latency_cycles"]
                    else ""
                ),
            }
        )
    write_csv(COMPARISON_OUT, comparison, list(comparison[0].keys()))

print(f"runs={len(rows)} groups={len(summary)}")
print(f"stable={sum(row['status'] == 'STABLE' for row in rows)} unstable={sum(row['status'] == 'UNSTABLE' for row in rows)} failed={sum(row['status'] == 'FAILED' for row in rows)}")
print(SUMMARY_OUT)

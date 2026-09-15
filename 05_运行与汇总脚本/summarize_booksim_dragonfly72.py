#!/usr/bin/env python3
import csv
import math
import re
import statistics
from pathlib import Path

BASE = Path.home() / "booksim2" / "formal_dragonfly72_unitlat_20260812"
RAW = BASE / "raw_runs.csv"
SUMMARY = BASE / "summary.csv"
NAME_RE = re.compile(
    r"^dragonfly72_(uniform|hotspotmix)_"
    r"(0\.02|0\.04|0\.06|0\.07|0\.075|0\.08|0\.10)_"
    r"seed(101|202|303|404|505)\.txt$"
)
LAT_RE = re.compile(r"^Packet latency average = ([0-9.eE+-]+) \(1 samples\)$", re.M)
INJ_RE = re.compile(r"^Injected packet rate average = ([0-9.eE+-]+) \(1 samples\)$", re.M)
ACC_RE = re.compile(r"^Accepted packet rate average = ([0-9.eE+-]+) \(1 samples\)$", re.M)


def final_value(pattern, text):
    values = pattern.findall(text)
    return float(values[-1]) if values else None


rows = []
for path in sorted((BASE / "logs").glob("*.txt")):
    match = NAME_RE.match(path.name)
    if not match:
        continue
    traffic, rate, seed = match.groups()
    text = path.read_text(errors="replace")
    unstable = "Simulation unstable" in text
    completed = "Total run time" in text or unstable
    latency = final_value(LAT_RE, text)
    injected = final_value(INJ_RE, text)
    accepted = final_value(ACC_RE, text)
    if not completed or (not unstable and (latency is None or accepted is None)):
        status = "FAILED"
    elif unstable:
        status = "UNSTABLE"
    else:
        status = "STABLE"
    rows.append({
        "topology": "dragonfly72",
        "traffic": traffic,
        "injection_rate": float(rate),
        "seed": int(seed),
        "status": status,
        "latency": latency if status == "STABLE" else None,
        "injected_rate": injected if status == "STABLE" else None,
        "accepted_rate": accepted if status == "STABLE" else None,
    })

if not rows:
    raise SystemExit(f"No matching logs found in {BASE / 'logs'}")

with RAW.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

groups = {}
for row in rows:
    key = (row["topology"], row["traffic"], row["injection_rate"])
    groups.setdefault(key, []).append(row)

summary = []
for key, group in sorted(groups.items()):
    stable = [row for row in group if row["status"] == "STABLE"]
    unstable = [row for row in group if row["status"] == "UNSTABLE"]
    failed = [row for row in group if row["status"] == "FAILED"]
    values = [row["latency"] for row in stable]
    mean = statistics.mean(values) if values else None
    std = statistics.stdev(values) if len(values) > 1 else (0.0 if values else None)
    ci95 = 2.7764451051977987 * std / math.sqrt(len(values)) if len(values) > 1 else (0.0 if values else None)
    if len(stable) == len(group):
        status = "STABLE"
    elif len(unstable) == len(group):
        status = "UNSTABLE"
    elif failed:
        status = "FAILED" if len(failed) == len(group) else "MIXED"
    else:
        status = "MIXED"
    summary.append({
        "topology": key[0],
        "traffic": key[1],
        "injection_rate": key[2],
        "total_runs": len(group),
        "stable_runs": len(stable),
        "unstable_runs": len(unstable),
        "failed_runs": len(failed),
        "status": status,
        "mean_latency": mean,
        "std_latency": std,
        "ci95_latency": ci95,
        "mean_accepted_rate": statistics.mean(row["accepted_rate"] for row in stable) if stable else None,
    })

with SUMMARY.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)

print(f"runs={len(rows)} groups={len(summary)}")
print(
    f"stable_runs={sum(row['status'] == 'STABLE' for row in rows)} "
    f"unstable_runs={sum(row['status'] == 'UNSTABLE' for row in rows)} "
    f"failed_runs={sum(row['status'] == 'FAILED' for row in rows)}"
)
print(SUMMARY)

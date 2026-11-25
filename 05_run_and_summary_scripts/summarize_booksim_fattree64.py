#!/usr/bin/env python3
import csv
import math
import re
import statistics
from pathlib import Path

BASE = Path.home() / "booksim2" / "formal_fattree64_20260812"
RAW = BASE / "raw_runs.csv"
SUMMARY = BASE / "summary.csv"
NAME_RE = re.compile(r"^fattree64_(uniform|hotspotmix)_(0\.01|0\.02|0\.04|0\.06|0\.07|0\.075|0\.08|0\.10)_seed(101|202|303|404|505)\.txt$")
LAT_RE = re.compile(r"^Packet latency average = ([0-9.eE+-]+) \(1 samples\)$", re.M)
INJ_RE = re.compile(r"^Injected packet rate average = ([0-9.eE+-]+) \(1 samples\)$", re.M)
ACC_RE = re.compile(r"^Accepted packet rate average = ([0-9.eE+-]+) \(1 samples\)$", re.M)

rows = []
for path in sorted((BASE / "logs").glob("*.txt")):
    match = NAME_RE.match(path.name)
    if not match:
        continue
    traffic, rate, seed = match.groups()
    text = path.read_text(errors="replace")
    unstable = "Simulation unstable" in text
    latency = LAT_RE.findall(text)
    injected = INJ_RE.findall(text)
    accepted = ACC_RE.findall(text)
    rows.append({
        "topology": "fattree",
        "traffic": traffic,
        "injection_rate": float(rate),
        "seed": int(seed),
        "status": "UNSTABLE" if unstable else "STABLE",
        "latency": float(latency[-1]) if latency and not unstable else None,
        "injected_rate": float(injected[-1]) if injected and not unstable else None,
        "accepted_rate": float(accepted[-1]) if accepted and not unstable else None,
    })

with RAW.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

groups = {}
for row in rows:
    groups.setdefault((row["topology"], row["traffic"], row["injection_rate"]), []).append(row)

summary = []
for key, group in sorted(groups.items()):
    stable = [row for row in group if row["status"] == "STABLE"]
    values = [row["latency"] for row in stable]
    mean = statistics.mean(values) if values else None
    std = statistics.stdev(values) if len(values) > 1 else (0.0 if values else None)
    ci95 = 2.7764451051977987 * std / math.sqrt(len(values)) if len(values) > 1 else (0.0 if values else None)
    summary.append({
        "topology": key[0],
        "traffic": key[1],
        "injection_rate": key[2],
        "total_runs": len(group),
        "stable_runs": len(stable),
        "unstable_runs": len(group) - len(stable),
        "status": "STABLE" if len(stable) == len(group) else ("UNSTABLE" if not stable else "MIXED"),
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
print(f"stable_runs={sum(row['status'] == 'STABLE' for row in rows)} unstable_runs={sum(row['status'] == 'UNSTABLE' for row in rows)}")
print(SUMMARY)

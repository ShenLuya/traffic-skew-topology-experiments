#!/usr/bin/env python3
import csv
import math
import re
import statistics
from pathlib import Path

BASE = Path.home() / "gem5" / "formal_20260812_100m"
RAW = BASE / "raw_runs.csv"
SUMMARY = BASE / "summary.csv"
SIM_TICKS = 100_000_000
SOURCE_CLOCK_TICKS = 1000
NETWORK_CLOCK_TICKS = 500
NODES = 64
SOURCE_CYCLES = SIM_TICKS / SOURCE_CLOCK_TICKS

RUN_RE = re.compile(
    r"^(FatTreeDirCorners|dragonfly)_(uniform_random|hotspotmix)_"
    r"rate(0\.01|0\.02|0\.04|0\.06|0\.08|0\.10)_seed(101|202|303|404|505)$"
)

STAT_PATTERNS = {
    "latency_ticks": re.compile(r"^system\.ruby\.network\.average_packet_latency\s+([0-9.eE+-]+)"),
    "packets_injected": re.compile(r"^system\.ruby\.network\.packets_injected::total\s+(\d+)"),
    "packets_received": re.compile(r"^system\.ruby\.network\.packets_received::total\s+(\d+)"),
}


def parse_stats(path):
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        for key, pattern in STAT_PATTERNS.items():
            match = pattern.match(line)
            if match:
                values[key] = float(match.group(1)) if key == "latency_ticks" else int(match.group(1))
    return values


rows = []
bad = []
for directory in sorted(p for p in BASE.iterdir() if p.is_dir()):
    match = RUN_RE.match(directory.name)
    if not match:
        continue
    topology, traffic, rate, seed = match.groups()
    log_path = directory / "run.log"
    stats_path = directory / "stats.txt"
    normal_exit = log_path.is_file() and "because Network Tester completed simCycles" in log_path.read_text(errors="replace")
    stats = parse_stats(stats_path) if stats_path.is_file() and stats_path.stat().st_size else {}
    valid = normal_exit and len(stats) == len(STAT_PATTERNS)
    if not valid:
        bad.append(directory.name)
    injected = stats.get("packets_injected")
    received = stats.get("packets_received")
    latency_ticks = stats.get("latency_ticks")
    rows.append({
        "topology": "fattree" if topology == "FatTreeDirCorners" else topology,
        "traffic": "uniform" if traffic == "uniform_random" else traffic,
        "injection_rate_requested": float(rate),
        "seed": int(seed),
        "normal_exit": normal_exit,
        "valid": valid,
        "latency_ticks": latency_ticks,
        "latency_network_cycles": latency_ticks / NETWORK_CLOCK_TICKS if latency_ticks is not None else None,
        "latency_ns": latency_ticks / 1000 if latency_ticks is not None else None,
        "packets_injected": injected,
        "packets_received": received,
        "packets_outstanding": injected - received if injected is not None and received is not None else None,
        "actual_injected_rate_per_node": injected / (NODES * SOURCE_CYCLES) if injected is not None else None,
        "actual_received_rate_per_node": received / (NODES * SOURCE_CYCLES) if received is not None else None,
    })

fields = list(rows[0].keys())
with RAW.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)


def sample_summary(values):
    mean = statistics.mean(values)
    if len(values) < 2:
        return mean, 0.0, 0.0
    std = statistics.stdev(values)
    # t(0.975, df=4) for five seeds.
    ci95 = 2.7764451051977987 * std / math.sqrt(len(values))
    return mean, std, ci95


summary_rows = []
groups = {}
for row in rows:
    key = (row["topology"], row["traffic"], row["injection_rate_requested"])
    groups.setdefault(key, []).append(row)

for key, group in sorted(groups.items()):
    valid_group = [row for row in group if row["valid"]]
    item = {
        "topology": key[0],
        "traffic": key[1],
        "injection_rate_requested": key[2],
        "total_runs": len(group),
        "valid_runs": len(valid_group),
    }
    for source, prefix in (
        ("latency_network_cycles", "latency_network_cycles"),
        ("latency_ns", "latency_ns"),
        ("actual_injected_rate_per_node", "actual_injected_rate_per_node"),
        ("actual_received_rate_per_node", "actual_received_rate_per_node"),
        ("packets_outstanding", "packets_outstanding"),
    ):
        values = [row[source] for row in valid_group]
        mean, std, ci95 = sample_summary(values) if values else (None, None, None)
        item[f"mean_{prefix}"] = mean
        item[f"std_{prefix}"] = std
        item[f"ci95_{prefix}"] = ci95
    summary_rows.append(item)

summary_fields = list(summary_rows[0].keys())
with SUMMARY.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=summary_fields)
    writer.writeheader()
    writer.writerows(summary_rows)

print(f"run_directories={len(rows)}")
print(f"valid_runs={sum(row['valid'] for row in rows)}")
print(f"invalid_runs={len(bad)}")
print(f"summary_groups={len(summary_rows)}")
if bad:
    print("invalid_names=" + ",".join(bad))
print(f"raw_csv={RAW}")
print(f"summary_csv={SUMMARY}")

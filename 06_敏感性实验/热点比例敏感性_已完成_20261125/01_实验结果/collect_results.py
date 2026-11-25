#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "run_manifest.csv"
ARCHIVE = ROOT / "historical_reference"

FINAL_PATTERNS = {
    "latency": re.compile(r"^Packet latency average = ([0-9.eE+\-]+) \(1 samples\)$", re.M),
    "injected_rate": re.compile(r"^Injected flit rate average = ([0-9.eE+\-]+) \(1 samples\)$", re.M),
    "accepted_rate": re.compile(r"^Accepted flit rate average = ([0-9.eE+\-]+) \(1 samples\)$", re.M),
}
RUNTIME_PATTERN = re.compile(r"^Total run time ([0-9.eE+\-]+)$", re.M)
SAMPLE_PATTERN = re.compile(r"^latency change\s*=", re.M)
T_CRIT_95_DF4 = 2.7764451051977987


def last_float(pattern: re.Pattern[str], text: str) -> float | None:
    matches = pattern.findall(text)
    return float(matches[-1]) if matches else None


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 180:
        raise RuntimeError(f"Expected 180 manifest rows, found {len(rows)}")
    run_ids = [row["run_id"] for row in rows]
    if len(set(run_ids)) != 180:
        raise RuntimeError("Manifest contains duplicate run_id values")
    return rows


def parse_run(row: dict[str, str]) -> dict[str, object]:
    log_path = ROOT / row["log_file"]
    config_path = ROOT / row["config_file"]
    if not log_path.is_file() or not config_path.is_file():
        raise RuntimeError(f"Missing config or log for {row['run_id']}")

    text = log_path.read_text(encoding="utf-8", errors="replace")
    config = config_path.read_text(encoding="utf-8", errors="replace")
    expected_lines = (
        f"topology = {row['topology']};",
        f"routing_function = {row['routing']};",
        f"traffic = hotspot_mix({{0,{row['hotspot_percentage']}}});",
        f"injection_rate = {row['injection_rate']};",
    )
    missing = [line for line in expected_lines if line not in config]
    if missing:
        raise RuntimeError(f"Config mismatch for {row['run_id']}: {missing}")
    if "Total run time" not in text:
        raise RuntimeError(f"Incomplete log for {row['run_id']}")

    sample_periods = len(SAMPLE_PATTERN.findall(text))
    threshold_exit = "Simulation unstable" in text
    if threshold_exit:
        status = "threshold_exit"
    elif sample_periods >= 10:
        status = "maximum_sample_stop"
    else:
        status = "converged_stop"

    values = {name: last_float(pattern, text) for name, pattern in FINAL_PATTERNS.items()}
    if status == "threshold_exit":
        if any(value is not None for value in values.values()):
            raise RuntimeError(f"Threshold exit unexpectedly has final statistics: {row['run_id']}")
    elif any(value is None for value in values.values()):
        raise RuntimeError(f"Final-statistic run is missing a metric: {row['run_id']}")

    runtime = last_float(RUNTIME_PATTERN, text)
    exit_path = log_path.with_suffix(".exitcode")
    exit_code = int(exit_path.read_text(encoding="utf-8").strip()) if exit_path.is_file() else None
    percentage = int(row["hotspot_percentage"])
    rate = float(row["injection_rate"])
    hotspot_fraction = percentage / 100.0
    hotspot_load = 64.0 * hotspot_fraction * rate
    rate_ratio = None
    if values["accepted_rate"] is not None and values["injected_rate"]:
        rate_ratio = values["accepted_rate"] / values["injected_rate"]

    return {
        "run_id": row["run_id"],
        "topology": row["topology"],
        "routing": row["routing"],
        "hotspot_percentage": percentage,
        "injection_rate": rate,
        "seed": int(row["seed"]),
        "status": status,
        "sample_periods": sample_periods,
        "latency": values["latency"],
        "injected_rate": values["injected_rate"],
        "accepted_rate": values["accepted_rate"],
        "accepted_over_injected": rate_ratio,
        "hotspot_offered_load": hotspot_load,
        "theoretical_rate_bound": 1.0 / (64.0 * hotspot_fraction),
        "above_destination_bound": hotspot_load > 1.0,
        "total_run_time_seconds": runtime,
        "process_exit_code": exit_code,
        "config_file": row["config_file"],
        "log_file": row["log_file"],
    }


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, int, float], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        key = (str(row["topology"]), int(row["hotspot_percentage"]), float(row["injection_rate"]))
        groups[key].append(row)

    output: list[dict[str, object]] = []
    for key in sorted(groups):
        group = groups[key]
        statuses = Counter(str(row["status"]) for row in group)
        final_rows = [row for row in group if row["latency"] is not None]
        latencies = [float(row["latency"]) for row in final_rows]
        ratios = [float(row["accepted_over_injected"]) for row in final_rows]
        mean_latency = statistics.mean(latencies) if latencies else None
        sd_latency = statistics.stdev(latencies) if len(latencies) > 1 else None
        ci95 = T_CRIT_95_DF4 * sd_latency / math.sqrt(5) if len(latencies) == 5 else None
        example = group[0]
        output.append(
            {
                "topology": key[0],
                "hotspot_percentage": key[1],
                "injection_rate": key[2],
                "n_runs": len(group),
                "n_converged_stops": statuses["converged_stop"],
                "n_maximum_sample_stops": statuses["maximum_sample_stop"],
                "n_threshold_exits": statuses["threshold_exit"],
                "n_with_final_statistics": len(final_rows),
                "mean_latency": mean_latency,
                "sd_latency": sd_latency,
                "ci95_half_width": ci95,
                "mean_accepted_over_injected": statistics.mean(ratios) if ratios else None,
                "hotspot_offered_load": example["hotspot_offered_load"],
                "theoretical_rate_bound": example["theoretical_rate_bound"],
                "above_destination_bound": example["above_destination_bound"],
            }
        )
    if len(output) != 36:
        raise RuntimeError(f"Expected 36 summary cells, found {len(output)}")
    return output


def load_historical() -> dict[tuple[str, float, int], dict[str, float]]:
    historical: dict[tuple[str, float, int], dict[str, float]] = {}
    for name in ("mesh_torus_raw_runs.csv", "fattree64_raw_runs.csv"):
        with (ARCHIVE / name).open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                if row["traffic"] != "hotspotmix":
                    continue
                rate = float(row["injection_rate"])
                if rate not in (0.02, 0.04):
                    continue
                if row["status"] not in ("OK", "STABLE"):
                    continue
                historical[(row["topology"], rate, int(row["seed"]))] = {
                    "latency": float(row["latency"]),
                    "injected_rate": float(row["injected_rate"]),
                    "accepted_rate": float(row["accepted_rate"]),
                }
    if len(historical) != 30:
        raise RuntimeError(f"Expected 30 historical comparison rows, found {len(historical)}")
    return historical


def compare_historical(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    historical = load_historical()
    comparisons: list[dict[str, object]] = []
    for row in rows:
        if row["hotspot_percentage"] != 20 or row["injection_rate"] not in (0.02, 0.04):
            continue
        key = (str(row["topology"]), float(row["injection_rate"]), int(row["seed"]))
        old = historical[key]
        exact = all(float(row[name]) == old[name] for name in ("latency", "injected_rate", "accepted_rate"))
        comparisons.append(
            {
                "topology": key[0],
                "injection_rate": key[1],
                "seed": key[2],
                "historical_latency": old["latency"],
                "new_latency": row["latency"],
                "historical_injected_rate": old["injected_rate"],
                "new_injected_rate": row["injected_rate"],
                "historical_accepted_rate": old["accepted_rate"],
                "new_accepted_rate": row["accepted_rate"],
                "exact_match": exact,
            }
        )
    if len(comparisons) != 30:
        raise RuntimeError(f"Expected 30 historical comparisons, found {len(comparisons)}")
    return comparisons


def main() -> None:
    manifest_rows = read_manifest()
    raw_rows = [parse_run(row) for row in manifest_rows]
    summary_rows = summarize(raw_rows)
    comparisons = compare_historical(raw_rows)

    write_csv(ROOT / "raw_runs.csv", raw_rows, list(raw_rows[0].keys()))
    write_csv(ROOT / "summary.csv", summary_rows, list(summary_rows[0].keys()))
    write_csv(ROOT / "historical_20pct_comparison.csv", comparisons, list(comparisons[0].keys()))

    statuses = Counter(str(row["status"]) for row in raw_rows)
    exit_codes = Counter(row["process_exit_code"] for row in raw_rows)
    exact_matches = sum(bool(row["exact_match"]) for row in comparisons)
    report_lines = [
        "HOTSPOT PERCENTAGE SENSITIVITY VERIFICATION",
        f"manifest_rows={len(manifest_rows)}",
        f"parsed_runs={len(raw_rows)}",
        f"summary_cells={len(summary_rows)}",
        f"converged_stops={statuses['converged_stop']}",
        f"maximum_sample_stops={statuses['maximum_sample_stop']}",
        f"threshold_exits={statuses['threshold_exit']}",
        f"process_exit_codes={dict(sorted(exit_codes.items(), key=lambda item: str(item[0])))}",
        f"historical_20pct_exact_matches={exact_matches}/30",
        "verification_status=VERIFIED" if exact_matches == 30 else "verification_status=CAUTION",
    ]
    report = "\n".join(report_lines) + "\n"
    (ROOT / "verification_report.txt").write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only integrity checks for the manuscript evidence archive."""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "paper_reproduction"
RATES = {0.02, 0.04, 0.06, 0.07, 0.075, 0.08, 0.10}
SEEDS = {101, 202, 303, 404, 505}
PILOT_SEEDS = {101, 202, 303}
COMPLETED = {"OK", "STABLE"}
TOLERANCE = 1e-7


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def final_number(text: str, label: str) -> float | None:
    values = re.findall(re.escape(label) + r"\s*=\s*([\d.eE+-]+)", text)
    return float(values[-1]) if values else None


def rate_tokens(value: float) -> list[str]:
    tokens = [str(value), f"{value:.2f}", f"{value:.3f}".rstrip("0")]
    return list(dict.fromkeys(tokens))


def main_log(topology: str, traffic: str, rate: float, seed: int) -> Path | None:
    if topology in {"mesh", "torus"}:
        folder = REPO / "02_BookSim主实验" / "01_Mesh_Torus_64端点_5种子" / "logs"
        stems = [f"{topology}_{traffic}_rate{token}_seed{seed}.txt" for token in rate_tokens(rate)]
    else:
        folder = REPO / "02_BookSim主实验" / "02_FatTree_64端点_5种子" / "logs"
        stems = [f"fattree64_{traffic}_{token}_seed{seed}.txt" for token in rate_tokens(rate)]
    return next((folder / stem for stem in stems if (folder / stem).is_file()), None)


def compare_metric(errors: list[str], path: Path, field: str, archived: str, observed: float | None) -> None:
    if observed is None or abs(float(archived) - observed) > TOLERANCE:
        errors.append(f"metric mismatch: {path.relative_to(REPO)} {field}: CSV={archived}, log={observed}")


def check_manifest(errors: list[str]) -> int:
    manifest = REPO / "SHA256SUMS-paper.txt"
    if not manifest.is_file():
        errors.append("missing SHA256SUMS-paper.txt")
        return 0
    checked = 0
    for line_number, raw in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not raw or raw.startswith("#"):
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw)
        if not match:
            errors.append(f"invalid checksum line {line_number}")
            continue
        expected, relative = match.groups()
        path = REPO / Path(relative)
        if not path.is_file():
            errors.append(f"checksum target missing: {relative}")
        elif sha256(path) != expected:
            errors.append(f"checksum mismatch: {relative}")
        checked += 1
    return checked


def main() -> int:
    errors: list[str] = []

    archived_mt = REPO / "01_最终汇总" / "mesh_torus_raw_runs.csv"
    archived_ft = REPO / "01_最终汇总" / "fattree64_raw_runs.csv"
    archived_pilot = REPO / "05_补充实验_热点位置_20260915" / "raw_runs.csv"
    copies = [
        (archived_mt, PAPER / "data" / "mesh_torus_raw_runs.csv"),
        (archived_ft, PAPER / "data" / "fattree64_raw_runs.csv"),
        (archived_pilot, PAPER / "data" / "position_raw_runs.csv"),
    ]
    for source, copy in copies:
        if source.read_bytes() != copy.read_bytes():
            errors.append(f"paper data copy differs from archive source: {copy.relative_to(REPO)}")

    mt_rows = read_csv(archived_mt)
    ft_rows = [row for row in read_csv(archived_ft) if float(row["injection_rate"]) in RATES]
    main_rows = mt_rows + ft_rows
    if len(mt_rows) != 140:
        errors.append(f"expected 140 Mesh/Torus attempts, found {len(mt_rows)}")
    if len(ft_rows) != 70:
        errors.append(f"expected 70 paper-rate Fat-Tree attempts, found {len(ft_rows)}")
    if len(main_rows) != 210:
        errors.append(f"expected 210 main attempts, found {len(main_rows)}")

    groups: dict[tuple[str, str, float], list[dict[str, str]]] = defaultdict(list)
    status_counts: Counter[str] = Counter()
    for row in main_rows:
        topology = row["topology"]
        traffic = row["traffic"]
        rate = float(row["injection_rate"])
        seed = int(row["seed"])
        groups[(topology, traffic, rate)].append(row)
        path = main_log(topology, traffic, rate, seed)
        if path is None:
            errors.append(f"missing main log: {topology}/{traffic}/{rate}/{seed}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        log_completed = "Simulation unstable" not in text and final_number(text, "Packet latency average") is not None
        csv_completed = row["status"] in COMPLETED
        if log_completed != csv_completed:
            errors.append(f"status mismatch: {path.relative_to(REPO)} CSV={row['status']}")
        status_counts["completed" if csv_completed else "threshold_exit"] += 1
        if csv_completed:
            compare_metric(errors, path, "latency", row["latency"], final_number(text, "Packet latency average"))
            compare_metric(errors, path, "injected_rate", row["injected_rate"], final_number(text, "Injected flit rate average"))
            compare_metric(errors, path, "accepted_rate", row["accepted_rate"], final_number(text, "Accepted flit rate average"))

    expected_cells = {(top, traffic, rate) for top in ("mesh", "torus", "fattree") for traffic in ("uniform", "hotspotmix") for rate in RATES}
    if set(groups) != expected_cells:
        errors.append("main factorial cells do not match 3 topologies x 2 traffic patterns x 7 rates")
    for key, rows in groups.items():
        if {int(row["seed"]) for row in rows} != SEEDS or len(rows) != 5:
            errors.append(f"main seed coverage mismatch: {key}")

    pilot_rows = read_csv(archived_pilot)
    if len(pilot_rows) != 54:
        errors.append(f"expected 54 pilot attempts, found {len(pilot_rows)}")
    pilot_groups: dict[tuple[str, int, float], list[dict[str, str]]] = defaultdict(list)
    pilot_status: Counter[str] = Counter()
    pilot_root = archived_pilot.parent
    for row in pilot_rows:
        key = (row["topology"], int(row["hotspot_node"]), float(row["injection_rate"]))
        pilot_groups[key].append(row)
        path = pilot_root / Path(row["log_file"].replace("\\", "/"))
        if not path.is_file():
            errors.append(f"missing pilot log: {path.relative_to(REPO)}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        log_completed = "Simulation unstable" not in text and final_number(text, "Packet latency average") is not None
        csv_completed = row["status"] in COMPLETED
        if log_completed != csv_completed:
            errors.append(f"pilot status mismatch: {path.relative_to(REPO)}")
        pilot_status["completed" if csv_completed else "threshold_exit"] += 1
        if csv_completed:
            compare_metric(errors, path, "latency_cycles", row["latency_cycles"], final_number(text, "Packet latency average"))
            compare_metric(errors, path, "injected_rate", row["injected_rate"], final_number(text, "Injected flit rate average"))
            compare_metric(errors, path, "accepted_rate", row["accepted_rate"], final_number(text, "Accepted flit rate average"))

    expected_pilot = {(top, node, rate) for top in ("mesh", "torus", "fattree") for node in (3, 27) for rate in (0.06, 0.075, 0.08)}
    if set(pilot_groups) != expected_pilot:
        errors.append("pilot factorial cells do not match 3 topologies x 2 nodes x 3 rates")
    for key, rows in pilot_groups.items():
        if {int(row["seed"]) for row in rows} != PILOT_SEEDS or len(rows) != 3:
            errors.append(f"pilot seed coverage mismatch: {key}")

    manifest_rows = read_csv(REPO / "02_BookSim主实验" / "01_Mesh_Torus_64端点_5种子" / "run_manifest.csv")
    if len(manifest_rows) != 140:
        errors.append(f"expected 140 Mesh/Torus manifest rows, found {len(manifest_rows)}")
    mt_root = REPO / "02_BookSim主实验" / "01_Mesh_Torus_64端点_5种子"
    for topology in ("mesh", "torus"):
        for traffic in ("uniform", "hotspotmix"):
            log = main_log(topology, traffic, 0.02, 101)
            if log is None:
                continue
            text = log.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"BEGIN Configuration File:.*?\n(.*?)\nEND Configuration File:", text, re.DOTALL)
            suffix = "uniform" if traffic == "uniform" else "hotspotmix_node0_20pct"
            config = mt_root / "configs" / f"{topology}_{suffix}_base.conf"
            if not match or match.group(1).strip() != config.read_text(encoding="utf-8").strip():
                errors.append(f"recovered base config does not match embedded log header: {config.relative_to(REPO)}")

    hash_entries = check_manifest(errors)
    summary = {
        "main_attempts": len(main_rows),
        "main_completed": status_counts["completed"],
        "main_threshold_exits": status_counts["threshold_exit"],
        "pilot_attempts": len(pilot_rows),
        "pilot_completed": pilot_status["completed"],
        "pilot_threshold_exits": pilot_status["threshold_exit"],
        "checksum_entries": hash_entries,
    }
    for key, value in summary.items():
        print(f"{key}={value}")
    if errors:
        print(f"FAILED ({len(errors)} errors)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

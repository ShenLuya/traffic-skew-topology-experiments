#!/usr/bin/env python3
"""Build the checksum list for paper-relevant evidence and tooling."""

import hashlib
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "SHA256SUMS-paper.txt"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def paper_rate(path: Path) -> bool:
    return "_0.01_" not in path.name


def main() -> None:
    paths: set[Path] = set()
    for name in (
        "README.md",
        "REPRODUCIBILITY.md",
        "requirements.txt",
        "CITATION.cff",
        "LICENSE_SELECTION_REQUIRED.md",
        "请先看_目录说明.txt",
    ):
        paths.add(REPO / name)

    paths.update(
        path
        for path in (REPO / "paper_reproduction").rglob("*")
        if path.is_file()
        and "generated" not in path.parts
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    )
    paths.update(
        {
            REPO / "01_最终汇总" / "main_64endpoint_summary.csv",
            REPO / "01_最终汇总" / "mesh_torus_raw_runs.csv",
            REPO / "01_最终汇总" / "fattree64_raw_runs.csv",
        }
    )

    mt = REPO / "02_BookSim主实验" / "01_Mesh_Torus_64端点_5种子"
    for name in ("README.md", "raw_runs.csv", "summary.csv", "run_manifest.csv", "run_from_manifest.sh", "build_run_manifest.py"):
        paths.add(mt / name)
    paths.update(path for path in (mt / "configs").glob("*.conf") if path.is_file())
    paths.update(path for path in (mt / "logs").glob("*.txt") if path.is_file())

    ft = REPO / "02_BookSim主实验" / "02_FatTree_64端点_5种子"
    paths.update(path for path in (ft / "configs").glob("*.conf") if path.is_file() and paper_rate(path))
    paths.update(path for path in (ft / "logs").glob("*.txt") if path.is_file() and paper_rate(path))

    pilot = REPO / "05_补充实验_热点位置_20260915"
    for name in ("README.md", "raw_runs.csv", "summary.csv", "comparison_with_node0.csv", "run_hotspot_position_pilot.sh", "summarize_hotspot_position_pilot.py"):
        paths.add(pilot / name)
    paths.update(path for path in (pilot / "configs").glob("*.conf") if path.is_file())
    paths.update(path for path in (pilot / "logs").glob("*.txt") if path.is_file())
    paths.update(path for path in (pilot / "booksim_hotspot_mix_source").rglob("*") if path.is_file())

    sensitivity = REPO / "06_敏感性实验" / "热点比例敏感性_已完成_20261125"
    paths.update(
        path
        for path in sensitivity.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}
    )

    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit("missing checksum inputs:\n" + "\n".join(str(path) for path in missing))
    lines = ["# SHA-256 manifest for paper-relevant evidence and reproduction tooling"]
    for path in sorted(paths, key=lambda item: item.relative_to(REPO).as_posix()):
        relative = path.relative_to(REPO).as_posix()
        lines.append(f"{digest(path)}  {relative}")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(paths)} entries to {OUTPUT}")


if __name__ == "__main__":
    main()

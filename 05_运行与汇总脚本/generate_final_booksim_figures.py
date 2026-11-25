#!/usr/bin/env python3
import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

BASE = Path(os.environ.get("BOOKSIM_RESULTS_DIR", Path(__file__).resolve().parents[1] / "01_最终汇总"))
MAIN = BASE / "main_64endpoint_summary.csv"
ALL = BASE / "all_topologies_summary.csv"
SCAN = BASE / "dragonfly72_hotspot_boundary_scan.csv"

COLORS = {"fattree": "#16847A", "mesh": "#D14E3F", "torus": "#2868A9", "dragonfly72": "#7258A6"}
LABELS = {"fattree": "Fat-Tree", "mesh": "Mesh", "torus": "Torus", "dragonfly72": "Dragonfly (72 endpoints)"}
MARKERS = {"fattree": "s", "mesh": "o", "torus": "^", "dragonfly72": "D"}


def load(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value):
    return float(value) if value not in (None, "") else np.nan


def format_axis(ax, title, ymax=None):
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Injection rate (flits/node/cycle)")
    ax.set_ylabel("Mean packet latency (cycles)")
    ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    if ymax is not None:
        ax.set_ylim(0, ymax)


def plot_series(ax, rows, topology, traffic):
    selected = sorted(
        (row for row in rows if row["topology"] == topology and row["traffic"] == traffic),
        key=lambda row: float(row["injection_rate"]),
    )
    stable = [row for row in selected if row["status"] == "STABLE"]
    x = [float(row["injection_rate"]) for row in stable]
    y = [number(row["mean_latency_cycles"]) for row in stable]
    ci = [number(row["ci95_latency_cycles"]) for row in stable]
    ax.errorbar(
        x,
        y,
        yerr=ci,
        label=LABELS[topology],
        color=COLORS[topology],
        marker=MARKERS[topology],
        markersize=5,
        linewidth=1.8,
        capsize=3,
    )
    unstable_x = [float(row["injection_rate"]) for row in selected if row["status"] == "UNSTABLE"]
    if unstable_x:
        top = ax.get_ylim()[1]
        tier = {"fattree": 0.94, "mesh": 0.90, "torus": 0.86, "dragonfly72": 0.94}[topology]
        ax.scatter(unstable_x, [top * tier] * len(unstable_x), marker="x", s=48, linewidths=2, color=COLORS[topology])


def save(fig, stem):
    fig.savefig(BASE / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(BASE / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


main_rows = load(MAIN)
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2), constrained_layout=True)
format_axis(axes[0], "(a) Uniform traffic, 64 endpoints", ymax=36)
for topology in ("fattree", "mesh", "torus"):
    plot_series(axes[0], main_rows, topology, "uniform")
axes[0].legend(frameon=False, fontsize=9, loc="upper left")

format_axis(axes[1], "(b) 20% hotspot traffic, 64 endpoints", ymax=110)
for topology in ("fattree", "mesh", "torus"):
    plot_series(axes[1], main_rows, topology, "hotspotmix")
axes[1].text(0.098, 106, "colored x = unstable", ha="right", va="top", fontsize=8, color="#4B5563")
save(fig, "figure_main_64endpoint_latency")

all_rows = load(ALL)
dragonfly_rows = [row for row in all_rows if row["topology"] == "dragonfly72"]
scan_rows = load(SCAN)
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2), constrained_layout=True)
format_axis(axes[0], "(a) Dragonfly uniform traffic, 72 endpoints", ymax=19)
plot_series(axes[0], dragonfly_rows, "dragonfly72", "uniform")
axes[0].legend(frameon=False, fontsize=9, loc="upper left")

format_axis(axes[1], "(b) Dragonfly 20% hotspot traffic, 72 endpoints", ymax=145)
plot_series(axes[1], dragonfly_rows, "dragonfly72", "hotspotmix")
unstable_scan = [float(row["injection_rate"]) for row in scan_rows if row["status"] == "UNSTABLE"]
axes[1].scatter(unstable_scan, [136] * len(unstable_scan), marker="x", s=52, linewidths=2, color=COLORS["dragonfly72"], label="Unstable boundary scan (seed 101)")
axes[1].legend(frameon=False, fontsize=8, loc="upper left")
axes[1].text(0.098, 8, "0.04 mean has a wide 95% CI near saturation", ha="right", va="bottom", fontsize=8, color="#4B5563")
save(fig, "figure_supplement_dragonfly72_latency")

print(BASE / "figure_main_64endpoint_latency.png")
print(BASE / "figure_supplement_dragonfly72_latency.png")

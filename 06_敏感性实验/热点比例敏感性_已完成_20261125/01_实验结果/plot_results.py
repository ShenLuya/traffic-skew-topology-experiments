#!/usr/bin/env python3
"""Plot the audited hotspot-percentage sensitivity experiment.

Final statistics from maximum-sample stops are shown as finite-run estimates
with open markers. Threshold exits are shown only as status annotations; they
are never converted into latency values.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter


ROOT = Path(__file__).resolve().parent
SUMMARY = ROOT / "summary.csv"
FIGURES = ROOT / "figures"

TOPOLOGIES = ["mesh", "torus", "fattree"]
TITLES = {
    "mesh": "Mesh–dor",
    "torus": "Torus–min_adapt",
    "fattree": "Fat-Tree–nca",
}
RATES = [0.02, 0.03, 0.04]
COLORS = {0.02: "#0072B2", 0.03: "#E69F00", 0.04: "#009E73"}
MARKERS = {0.02: "o", 0.03: "s", 0.04: "^"}


def read_summary() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with SUMMARY.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            row: dict[str, object] = dict(raw)
            for key in (
                "hotspot_percentage",
                "n_runs",
                "n_converged_stops",
                "n_maximum_sample_stops",
                "n_threshold_exits",
                "n_with_final_statistics",
            ):
                row[key] = int(raw[key])
            for key in (
                "injection_rate",
                "hotspot_offered_load",
                "theoretical_rate_bound",
            ):
                row[key] = float(raw[key])
            for key in ("mean_latency", "ci95_half_width"):
                row[key] = float(raw[key]) if raw[key] else None
            rows.append(row)
    return rows


def main() -> None:
    rows = read_summary()
    FIGURES.mkdir(exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 10,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.35), sharey=True)
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.22, top=0.79, wspace=0.10)

    for ax, topology in zip(axes, TOPOLOGIES):
        topology_rows = [row for row in rows if row["topology"] == topology]

        # At lambda=0.04, 39.0625% is the analytical destination-load bound.
        bound_pct = 100.0 / (64.0 * 0.04)
        ax.axvspan(bound_pct, 42, color="#D55E00", alpha=0.08, zorder=0)
        ax.axvline(bound_pct, color="#D55E00", linewidth=0.9, linestyle="--", zorder=1)

        for rate in RATES:
            rate_rows = sorted(
                [row for row in topology_rows if row["injection_rate"] == rate],
                key=lambda row: row["hotspot_percentage"],
            )

            # Connect only cells whose five seeds all reached convergence.
            converged = [
                row
                for row in rate_rows
                if row["mean_latency"] is not None
                and row["n_converged_stops"] == row["n_runs"]
            ]
            ax.errorbar(
                [row["hotspot_percentage"] for row in converged],
                [row["mean_latency"] for row in converged],
                yerr=[row["ci95_half_width"] for row in converged],
                color=COLORS[rate],
                marker=MARKERS[rate],
                markersize=4.5,
                linewidth=1.4,
                capsize=2.2,
                label=f"Injection rate {rate:.2f}",
                zorder=3,
            )

            # Finite-run estimates are intentionally not connected to the
            # converged line and use open diamonds.
            finite = [
                row
                for row in rate_rows
                if row["mean_latency"] is not None
                and row["n_converged_stops"] < row["n_runs"]
            ]
            for row in finite:
                yerr = row["ci95_half_width"]
                ax.errorbar(
                    [row["hotspot_percentage"]],
                    [row["mean_latency"]],
                    yerr=None if yerr is None else [yerr],
                    color=COLORS[rate],
                    marker="D",
                    markerfacecolor="white",
                    markeredgewidth=1.4,
                    markersize=5.5,
                    linestyle="none",
                    capsize=2.2,
                    zorder=4,
                )
                status = (
                    f"{row['n_maximum_sample_stops']} max-sample"
                    + (
                        f"\n{row['n_threshold_exits']} threshold exits"
                        if row["n_threshold_exits"]
                        else ""
                    )
                )
                ax.annotate(
                    status,
                    xy=(row["hotspot_percentage"], row["mean_latency"]),
                    xytext=(-5, 10),
                    textcoords="offset points",
                    ha="right",
                    va="bottom",
                    fontsize=7.2,
                    color="#333333",
                )
                if row["n_threshold_exits"]:
                    # Position is in axes coordinates so the cross communicates
                    # status only, not a numerical latency of 500 cycles.
                    ax.scatter(
                        [row["hotspot_percentage"]],
                        [0.94],
                        transform=ax.get_xaxis_transform(),
                        marker="x",
                        color="#CC3311",
                        s=32,
                        linewidths=1.5,
                        clip_on=False,
                        zorder=5,
                    )

        ax.set_title(TITLES[topology])
        ax.set_xlim(8, 42)
        ax.set_xticks([10, 20, 30, 40])
        ax.set_xlabel("Hotspot traffic share (%)")
        ax.set_yscale("log")
        ax.set_ylim(10, 270)
        ax.set_yticks([10, 20, 50, 100, 200])
        ax.yaxis.set_major_formatter(ScalarFormatter())
        ax.grid(axis="y", which="major", color="#D9D9D9", linewidth=0.7)
        ax.grid(axis="x", which="major", color="#EEEEEE", linewidth=0.5)
        ax.set_axisbelow(True)

    axes[0].set_ylabel("Mean packet latency (cycles, log scale)")

    rate_handles = [
        Line2D(
            [0],
            [0],
            color=COLORS[rate],
            marker=MARKERS[rate],
            linewidth=1.4,
            markersize=4.5,
            label=f"Injection rate {rate:.2f}",
        )
        for rate in RATES
    ]
    status_handles = [
        Line2D(
            [0],
            [0],
            color="#444444",
            marker="D",
            markerfacecolor="white",
            linestyle="none",
            markersize=5.5,
            label="Finite-run estimate (maximum-sample stop)",
        ),
        Line2D(
            [0],
            [0],
            color="#CC3311",
            marker="x",
            linestyle="none",
            markersize=6,
            label="At least one threshold exit (no latency assigned)",
        ),
    ]
    fig.legend(
        handles=rate_handles + status_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        ncol=3,
        frameon=False,
        columnspacing=1.4,
        handletextpad=0.5,
    )
    fig.text(
        0.5,
        0.08,
        "Dashed boundary: at injection rate 0.04, hotspot destination load exceeds 1 flit/cycle above 39.06%.",
        ha="center",
        fontsize=8,
        color="#5A321E",
    )

    png_path = FIGURES / "hotspot_percentage_latency.png"
    pdf_path = FIGURES / "hotspot_percentage_latency.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)

    print(f"wrote={png_path}")
    print(f"wrote={pdf_path}")


if __name__ == "__main__":
    main()

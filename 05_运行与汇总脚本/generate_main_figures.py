"""RETIRED: historical mixed-simulator figure prototype.

This file is retained only to document an earlier analysis attempt. It mixes
BookSim Mesh/Torus data with gem5 Fat-Tree/Dragonfly data and is not valid for
the manuscript. Use ``paper_reproduction/redraw_figures.py`` instead.
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(os.environ.get("LEGACY_RESULTS_ROOT", Path(__file__).resolve().parent / "legacy_inputs"))
DATA_ROOT = ROOT / "paper_results_clean"
OUT = DATA_ROOT / "final_main_figures_clean"

BOOKSIM_SUMMARY = (
    DATA_ROOT
    / "booksim_mesh_torus"
    / "clean_mesh_torus_hotspot_runs_3rep"
    / "booksim_mesh_torus_3rep_summary.csv"
)
FATTREE_CSV = DATA_ROOT / "gem5_fattree" / "fattree_gem5_results.csv"
DRAGONFLY_CSV = DATA_ROOT / "gem5_dragonfly" / "dragonfly_results.csv"


COLORS = {
    "Mesh": "#1f77b4",
    "Torus": "#d62728",
    "Fat-Tree": "#2ca02c",
    "Dragonfly": "#9467bd",
}
MARKERS = {
    "Mesh": "o",
    "Torus": "s",
    "Fat-Tree": "^",
    "Dragonfly": "D",
}


def setup_style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.labelsize": 10,
            "axes.titlesize": 10,
            "legend.fontsize": 9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.grid": True,
            "grid.alpha": 0.28,
            "grid.linestyle": "--",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.bbox": "tight",
            "savefig.dpi": 300,
        }
    )


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)


def load_booksim():
    df = pd.read_csv(BOOKSIM_SUMMARY)
    df["Topology"] = df["topology"].map({"mesh": "Mesh", "torus": "Torus"})
    df["Traffic"] = df["traffic"].map({"uniform": "Uniform", "hotspot": "Hotspot"})
    df = df.rename(
        columns={
            "injection_rate": "Injection Rate",
            "packet_latency_mean": "Avg Packet Latency",
            "accepted_flit_rate_mean": "Accepted Flit Rate",
        }
    )
    return df


def load_gem5():
    fat = pd.read_csv(FATTREE_CSV)
    fat["Topology"] = "Fat-Tree"
    drag = pd.read_csv(DRAGONFLY_CSV)
    drag["Topology"] = "Dragonfly"
    df = pd.concat([fat, drag], ignore_index=True)
    df = df.rename(
        columns={
            "Traffic Type": "Traffic",
            "Injection Rate": "Injection Rate",
            "Avg Packet Latency": "Avg Packet Latency",
        }
    )
    df["Traffic"] = df["Traffic"].replace({"Hotspot-like": "Hotspot-like"})
    return df


def plot_booksim_latency(booksim):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), sharex=True)
    panels = [("Uniform", "Uniform traffic"), ("Hotspot", "Hotspot traffic")]

    for ax, (traffic, label) in zip(axes, panels):
        sub = booksim[booksim["Traffic"] == traffic]
        for topo in ["Mesh", "Torus"]:
            d = sub[sub["Topology"] == topo].sort_values("Injection Rate")
            ax.plot(
                d["Injection Rate"],
                d["Avg Packet Latency"],
                marker=MARKERS[topo],
                linewidth=1.9,
                markersize=4.8,
                color=COLORS[topo],
                label=topo,
            )
        ax.set_title(label)
        ax.set_xlabel("Injection rate (flits/node/cycle)")
        ax.set_xticks([0.02, 0.04, 0.06, 0.08, 0.10])
        ax.legend(frameon=False, loc="best")

    axes[0].set_ylabel("Average packet latency (cycles)")
    fig.tight_layout(w_pad=1.4)
    save(fig, "fig_main_booksim_mesh_torus_latency")


def plot_gem5_latency(gem5):
    rates = [0.02, 0.04, 0.06, 0.08, 0.10]
    df = gem5[gem5["Injection Rate"].isin(rates)].copy()

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), sharex=True, sharey=True)
    panels = [("Uniform", "Uniform traffic"), ("Hotspot-like", "Hotspot-like traffic")]

    for ax, (traffic, label) in zip(axes, panels):
        sub = df[df["Traffic"] == traffic]
        for topo in ["Fat-Tree", "Dragonfly"]:
            d = sub[sub["Topology"] == topo].sort_values("Injection Rate")
            ax.plot(
                d["Injection Rate"],
                d["Avg Packet Latency"],
                marker=MARKERS[topo],
                linewidth=1.9,
                markersize=4.8,
                color=COLORS[topo],
                label=topo,
            )
        ax.set_title(label)
        ax.set_xlabel("Injection rate (flits/node/cycle)")
        ax.set_xticks(rates)
        ax.legend(frameon=False, loc="best")

    axes[0].set_ylabel("Average packet latency (cycles)")
    fig.tight_layout(w_pad=1.4)
    save(fig, "fig_main_gem5_fattree_dragonfly_latency")


def compute_ldf(booksim, gem5):
    records = []

    for topo in ["Mesh", "Torus"]:
        uni = (
            booksim[(booksim["Topology"] == topo) & (booksim["Traffic"] == "Uniform")]
            .set_index("Injection Rate")["Avg Packet Latency"]
        )
        hot = (
            booksim[(booksim["Topology"] == topo) & (booksim["Traffic"] == "Hotspot")]
            .set_index("Injection Rate")["Avg Packet Latency"]
        )
        for rate in sorted(set(uni.index) & set(hot.index)):
            records.append(
                {
                    "Topology": topo,
                    "Injection Rate": rate,
                    "LDF": float(hot.loc[rate] / uni.loc[rate]),
                }
            )

    rates = [0.02, 0.04, 0.06, 0.08, 0.10]
    for topo in ["Fat-Tree", "Dragonfly"]:
        uni = (
            gem5[(gem5["Topology"] == topo) & (gem5["Traffic"] == "Uniform")]
            .set_index("Injection Rate")["Avg Packet Latency"]
        )
        hot = (
            gem5[(gem5["Topology"] == topo) & (gem5["Traffic"] == "Hotspot-like")]
            .set_index("Injection Rate")["Avg Packet Latency"]
        )
        for rate in rates:
            records.append(
                {
                    "Topology": topo,
                    "Injection Rate": rate,
                    "LDF": float(hot.loc[rate] / uni.loc[rate]),
                }
            )

    return pd.DataFrame(records)


def plot_ldf(ldf):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))

    for topo in ["Mesh", "Torus", "Fat-Tree", "Dragonfly"]:
        d = ldf[ldf["Topology"] == topo].sort_values("Injection Rate")
        ax.plot(
            d["Injection Rate"],
            d["LDF"],
            marker=MARKERS[topo],
            linewidth=2.0,
            markersize=5.0,
            color=COLORS[topo],
            label=topo,
        )

    ax.axhline(1.0, color="#555555", linewidth=1.0, linestyle=":", alpha=0.9)
    ax.set_xlabel("Injection rate (flits/node/cycle)")
    ax.set_ylabel("LDF (hotspot / uniform)")
    ax.set_xticks([0.02, 0.04, 0.06, 0.08, 0.10])
    ax.set_ylim(0, max(19.5, ldf["LDF"].max() * 1.08))
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.subplots_adjust(left=0.14, right=0.98, bottom=0.18, top=0.95)
    save(fig, "fig_main_all_topology_ldf")


def main():
    raise SystemExit(
        "RETIRED SCRIPT: mixed BookSim/gem5 figures are not comparable. "
        "Use paper_reproduction/redraw_figures.py."
    )
    setup_style()
    booksim = load_booksim()
    gem5 = load_gem5()

    plot_booksim_latency(booksim)
    plot_gem5_latency(gem5)
    ldf = compute_ldf(booksim, gem5)
    ldf.to_csv(OUT / "main_all_topology_ldf_values.csv", index=False)
    plot_ldf(ldf)

    print(f"Saved figures to: {OUT}")
    for path in sorted(OUT.glob("fig_main_*.*")):
        print(path)


if __name__ == "__main__":
    main()

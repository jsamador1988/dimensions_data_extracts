"""Shared plotting primitives for paper_first_draft figures.

Layouts:
  make_grid(nrows, ncols) -> (fig, axes)
  plot_region_lines(ax, shares_df, title="", ylim=None)
  plot_country_lines(ax, shares_df, country_codes, title="")
  save(fig, path) -> writes pdf + png + jpg at configured DPI

Styles come from config_apr16.yaml plot section.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml

_CFG = yaml.safe_load((Path(__file__).parent / "config_apr16.yaml").read_text())
PLOT = _CFG["plot"]
REGION_COLORS = _CFG["region_colors"]
REGION_LABELS = _CFG["region_labels"]
REGION_ORDER = _CFG["region_order"]

plt.rcParams.update({
    "font.family": PLOT["font_family"],
    "axes.titlesize": PLOT["title_size"],
    "axes.labelsize": PLOT["axis_label_size"],
    "legend.fontsize": PLOT["legend_size"],
    "xtick.labelsize": PLOT["tick_size"],
    "ytick.labelsize": PLOT["tick_size"],
})


def make_grid(nrows: int, ncols: int, figsize_per_panel=(4.0, 3.2)):
    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(ncols * figsize_per_panel[0], nrows * figsize_per_panel[1]),
        sharex=True,
    )
    if nrows == 1 and ncols == 1:
        axes = [[axes]]
    elif nrows == 1:
        axes = [axes]
    elif ncols == 1:
        axes = [[a] for a in axes]
    return fig, axes


def plot_region_lines(ax, shares_df: pd.DataFrame, title: str = "", ylim=None):
    for region in REGION_ORDER:
        if region not in shares_df.columns:
            continue
        ax.plot(
            shares_df.index, shares_df[region],
            label=REGION_LABELS.get(region, region),
            color=REGION_COLORS.get(region, "#333333"),
            linewidth=1.5,
        )
    ax.set_title(title)
    ax.set_ylabel("Share of world total")
    ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.5)
    if ylim is not None:
        ax.set_ylim(*ylim)


def plot_country_lines(ax, shares_df: pd.DataFrame, country_codes, title: str = ""):
    for c in country_codes:
        if c not in shares_df.columns:
            continue
        ax.plot(shares_df.index, shares_df[c], label=c, linewidth=1.2)
    ax.set_title(title)
    ax.set_ylabel("Share of world total")
    ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.5)


def legend_below(fig, axes_list, ncol: int = 5):
    """Single legend below the figure."""
    handles, labels = axes_list[0][0].get_legend_handles_labels()
    fig.legend(
        handles, labels,
        loc="lower center", ncol=ncol,
        bbox_to_anchor=(0.5, -0.03),
        frameon=False,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))


def save(fig, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dpi = PLOT["dpi"]
    fig.savefig(path.with_suffix(".pdf"), dpi=dpi, bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(path.with_suffix(".jpg"), dpi=dpi, bbox_inches="tight")
    plt.close(fig)

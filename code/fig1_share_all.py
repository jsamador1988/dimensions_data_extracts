"""Figure 1 (2x3): World share of pub/pat total + basic + top-5%, by NY region, 1980-2022.

Top row = publications, bottom row = patents. Columns: all / basic research / top 5%.
Top-left and top-right pub panels are the Nagaraj-Yao Fig 1b replication targets;
we expect a 3-5pp gap due to fractional (vs. random-selection) attribution and
document it in the figure note / outputs/validation/.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from common_regions import region_shares
from data_prep import load_config, load_panel, load_world
from plot_helpers import legend_below, make_grid, plot_region_lines, save


def main() -> int:
    cfg = load_config()
    panel = load_panel(cfg)
    world = load_world(cfg)

    fspec = cfg["figures"]["fig1"]
    yr = tuple(fspec["year_range"])

    fig, axes = make_grid(2, 3)
    for r, row in enumerate(fspec["rows"]):
        for c, col in enumerate(row["cols"]):
            shares = region_shares(
                panel, world,
                num_col=col["numerator"],
                denom_col=col["denominator"],
                year_range=yr,
            )
            plot_region_lines(axes[r][c], shares, title=col["title"])

    axes[0][0].set_title(f"{fspec['rows'][0]['label']}: " + axes[0][0].get_title())
    axes[1][0].set_title(f"{fspec['rows'][1]['label']}: " + axes[1][0].get_title())
    legend_below(fig, axes)

    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig1"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

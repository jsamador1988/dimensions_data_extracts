"""Figure 5 (1x2): World share of clinical trials, 1980-2022.

Col 1: total (any sponsor). Col 2: gov-sponsored subset.
Attribution: sponsor-organization country (fractional).
"""

from __future__ import annotations

from pathlib import Path

from common_regions import region_shares
from data_prep import load_config, load_panel, load_world
from plot_helpers import legend_below, make_grid, plot_region_lines, save


def main() -> int:
    cfg = load_config()
    panel, world = load_panel(cfg), load_world(cfg)
    fspec = cfg["figures"]["fig5"]
    yr = tuple(fspec["year_range"])

    fig, axes = make_grid(1, 2)
    for i, p in enumerate(fspec["panels"]):
        shares = region_shares(panel, world, p["numerator"], p["denominator"], yr)
        plot_region_lines(axes[0][i], shares, title=p["title"])
    legend_below(fig, axes)

    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig5"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

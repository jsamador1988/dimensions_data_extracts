"""Figure 4 (2x2): World share of grants, 1980-2022.

Top row: total / basic research. Bottom row: gov-funder / non-gov-funder.
Attribution: research-organization country (fractional), not funder country.
"""

from __future__ import annotations

from pathlib import Path

from common_regions import region_shares
from data_prep import load_config, load_panel, load_world
from plot_helpers import legend_below, make_grid, plot_region_lines, save


def main() -> int:
    cfg = load_config()
    panel, world = load_panel(cfg), load_world(cfg)
    fspec = cfg["figures"]["fig4"]
    yr = tuple(fspec["year_range"])

    fig, axes = make_grid(2, 2)
    panels = fspec["panels"]
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for i, p in enumerate(panels):
        r, c = positions[i]
        shares = region_shares(panel, world, p["numerator"], p["denominator"], yr)
        plot_region_lines(axes[r][c], shares, title=p["title"])
    legend_below(fig, axes)

    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig4"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

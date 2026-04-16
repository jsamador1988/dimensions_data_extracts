"""Figure 3 (2x3): World share of government-owned pubs/patents, 1980-2022.

Government-owned = whitelisted gov assignee/affiliation (dom_gov_assg_flag for patents,
w_public_prod for pubs). Universities are NOT considered government unless whitelisted.
"""

from __future__ import annotations

from pathlib import Path

from common_regions import region_shares
from data_prep import load_config, load_panel, load_world
from plot_helpers import legend_below, make_grid, plot_region_lines, save


def main() -> int:
    cfg = load_config()
    panel, world = load_panel(cfg), load_world(cfg)
    fspec = cfg["figures"]["fig3"]
    yr = tuple(fspec["year_range"])

    fig, axes = make_grid(2, 3)
    for r, row in enumerate(fspec["rows"]):
        for c, col in enumerate(row["cols"]):
            shares = region_shares(panel, world, col["numerator"], col["denominator"], yr)
            plot_region_lines(axes[r][c], shares, title=f"{row['label']}: {col['title']}" if c == 0 else col["title"])
    legend_below(fig, axes)

    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig3"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

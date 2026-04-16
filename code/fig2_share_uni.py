"""Figure 2 (2x3): World share of university-owned pubs/patents, 1980-2022."""

from __future__ import annotations

from pathlib import Path

from common_regions import region_shares
from data_prep import load_config, load_panel, load_world
from plot_helpers import legend_below, make_grid, plot_region_lines, save


def main() -> int:
    cfg = load_config()
    panel, world = load_panel(cfg), load_world(cfg)
    fspec = cfg["figures"]["fig2"]
    yr = tuple(fspec["year_range"])

    fig, axes = make_grid(2, 3)
    for r, row in enumerate(fspec["rows"]):
        for c, col in enumerate(row["cols"]):
            shares = region_shares(panel, world, col["numerator"], col["denominator"], yr)
            plot_region_lines(axes[r][c], shares, title=f"{row['label']}: {col['title']}" if c == 0 else col["title"])
    legend_below(fig, axes)

    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig2"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

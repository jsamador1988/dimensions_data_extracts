"""Figure 9 (1x3): Private patents with gov-funding (union of direct/RID/INST) as
share of worldwide patents for 14 countries with available data, 2000-2022.
Columns: all / top 5% (forward cites) / basic research.
"""

from __future__ import annotations

from pathlib import Path

from common_regions import country_shares
from data_prep import load_config, load_panel, load_world
from plot_helpers import make_grid, save


def main() -> int:
    cfg = load_config()
    panel, world = load_panel(cfg), load_world(cfg)
    fspec = cfg["figures"]["fig9"]
    yr = tuple(fspec["year_range"])
    countries = cfg["fig9_countries"]

    fig, axes = make_grid(1, 3)
    for i, p in enumerate(fspec["panels"]):
        shares = country_shares(panel, world, p["numerator"], p["denominator"], yr, countries)
        for c in countries:
            if c in shares.columns:
                axes[0][i].plot(shares.index, shares[c], label=c, linewidth=1.1)
        axes[0][i].set_title(p["title"])
        axes[0][i].set_ylabel("Share of world patents")
        axes[0][i].grid(True, linestyle="--", linewidth=0.3, alpha=0.5)

    axes[0][0].legend(loc="best", ncol=2, fontsize=7)
    fig.tight_layout()
    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig9"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

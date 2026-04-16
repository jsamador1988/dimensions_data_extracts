"""Figure 8 (1x3): Private publications with gov-funding (union of direct/RID/INST) as
share of worldwide publications, US/EU/China, 2000-2022.
Columns: all / top 5% journal / basic research.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from common_regions import REGION_COLORS, REGION_LABELS, annualize, classify
from data_prep import load_config, load_panel, load_world
from plot_helpers import make_grid, save


def main() -> int:
    cfg = load_config()
    panel = load_panel(cfg)
    world = load_world(cfg)
    fspec = cfg["figures"]["fig8"]
    yr = tuple(fspec["year_range"])
    panels = fspec["panels"]

    # Tag and aggregate by region
    p = panel.copy()
    p["ny_region"] = p["country_code"].map(classify)
    p = annualize(p, "quarter")
    p = p[(p["year"] >= yr[0]) & (p["year"] <= yr[1])]
    p = p[p["ny_region"].isin(["US", "EU", "CHINA"])]

    w = world.copy()
    w["year"] = pd.to_datetime(w["quarter"]).dt.year
    w = w[(w["year"] >= yr[0]) & (w["year"] <= yr[1])]

    fig, axes = make_grid(1, 3)
    for i, panel_spec in enumerate(panels):
        num = p.groupby(["year", "ny_region"])[panel_spec["numerator"]].sum().unstack("ny_region")
        denom = w.groupby("year")[panel_spec["denominator"]].sum()
        shares = num.div(denom, axis=0).reindex(columns=["US", "EU", "CHINA"], fill_value=0.0)

        for region in ["US", "EU", "CHINA"]:
            axes[0][i].plot(
                shares.index, shares[region],
                label=REGION_LABELS[region].split(" (")[0],
                color=REGION_COLORS[region], linewidth=1.5
            )
        axes[0][i].set_title(panel_spec["title"])
        axes[0][i].set_ylabel("Share of world publications")
        axes[0][i].grid(True, linestyle="--", linewidth=0.3, alpha=0.5)

    axes[0][0].legend(loc="best", fontsize=8)
    fig.tight_layout()
    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig8"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

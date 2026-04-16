"""Figure 6 (1x2): US patents -- gov-owned share | private-with-direct-gov-funding share.

Denominator for both panels = total US patents (pat_total_ctq filtered to US).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from common_regions import annualize
from data_prep import load_config, load_panel
from plot_helpers import make_grid, save


def main() -> int:
    cfg = load_config()
    panel = load_panel(cfg)
    fspec = cfg["figures"]["fig6"]
    yr = tuple(fspec["year_range"])

    us = panel[panel["country_code"] == "US"].copy()
    us = annualize(us, "quarter")
    us = us[(us["year"] >= yr[0]) & (us["year"] <= yr[1])]
    us_annual = us.groupby("year").sum(numeric_only=True)

    fig, axes = make_grid(1, 2)
    for i, p in enumerate(fspec["panels"]):
        share = us_annual[p["numerator"]] / us_annual["pat_total_ctq"]
        axes[0][i].plot(share.index, share, color="#1f77b4", linewidth=1.5)
        axes[0][i].set_title(p["title"])
        axes[0][i].set_ylabel("Share of US total patents")
        axes[0][i].grid(True, linestyle="--", linewidth=0.3, alpha=0.5)

    fig.tight_layout()
    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig6"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

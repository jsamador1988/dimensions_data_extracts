"""Figure 7 (2x2): US patents with 3-tier government-funding linkage.

Top-left:  pat_govfund_rid_ctq / pat_total_ctq  (researcher-ID linked)
Top-right: pat_govfund_inst_ctq / pat_total_ctq (institution linked)
Bottom-left:  validation overlay -- (RID+INST-only de-duped) vs (direct-only), both on one axis.
              If the method-linked share is comparable to the direct-link share,
              the linkage procedure is validated.
Bottom-right: pat_union3_govfund_ctq / pat_total_ctq (direct + RID + INST de-duplicated)

Denominator for all panels = total US patents.
"""

from __future__ import annotations

from pathlib import Path

from common_regions import annualize
from data_prep import load_config, load_panel
from plot_helpers import make_grid, save


def main() -> int:
    cfg = load_config()
    panel = load_panel(cfg)
    fspec = cfg["figures"]["fig7"]
    yr = tuple(fspec["year_range"])

    us = panel[panel["country_code"] == "US"].copy()
    us = annualize(us, "quarter")
    us = us[(us["year"] >= yr[0]) & (us["year"] <= yr[1])]
    us_annual = us.groupby("year").sum(numeric_only=True)
    denom = us_annual["pat_total_ctq"]

    fig, axes = make_grid(2, 2)

    # Top-left: RID
    axes[0][0].plot(denom.index, us_annual["pat_govfund_rid_ctq"] / denom, color="#1f77b4", linewidth=1.5)
    axes[0][0].set_title("Researcher-ID linked")

    # Top-right: INST
    axes[0][1].plot(denom.index, us_annual["pat_govfund_inst_ctq"] / denom, color="#2ca02c", linewidth=1.5)
    axes[0][1].set_title("Institution linked")

    # Bottom-left: validation overlay -- {RID-only + INST-only} vs direct
    # Using exclusive variants to avoid double-counting RID/INST overlap with each other
    rid_plus_inst = (us_annual["pat_govfund_rid_only_excl_ctq"] + us_annual["pat_govfund_inst_only_excl_ctq"]) / denom
    direct_only = us_annual["pat_govfund_direct_ctq"] / denom
    axes[1][0].plot(denom.index, rid_plus_inst, label="RID + INST (methods)", color="#d62728", linewidth=1.5)
    axes[1][0].plot(denom.index, direct_only,   label="Direct link",          color="#1f77b4", linewidth=1.5, linestyle="--")
    axes[1][0].set_title("Validation: methods vs. direct")
    axes[1][0].legend(loc="best", fontsize=8)

    # Bottom-right: union of 3
    axes[1][1].plot(denom.index, us_annual["pat_union3_govfund_ctq"] / denom, color="#8c564b", linewidth=1.5)
    axes[1][1].set_title("Union (direct + RID + INST, de-dup)")

    for row in axes:
        for ax in row:
            ax.set_ylabel("Share of US total patents")
            ax.grid(True, linestyle="--", linewidth=0.3, alpha=0.5)

    fig.tight_layout()
    out = Path(__file__).parent.parent / "outputs" / "figures" / "fig7"
    save(fig, out)
    print(f"Wrote {out}.{{pdf,png,jpg}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

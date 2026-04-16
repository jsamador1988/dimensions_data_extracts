"""One-shot: copy Empirics/dataform/definitions/*.sqlx into paper_first_draft/dataform/definitions/,
then print a diff so the operator can see what would overwrite. Use this to refresh the fork
after upstream Dataform changes land in the main Empirics pipeline.

Safe-guards: never overwrites files in paper_first_draft that have "apr16" additions
(the new SQLX from the plan); only refreshes files that are identical to or older than Empirics.
"""

from __future__ import annotations

import argparse
import difflib
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent      # PF_Dimensions/
SRC  = ROOT / "Empirics" / "dataform" / "definitions"
DST  = ROOT / "paper_first_draft" / "dataform" / "definitions"

APR16_NEW = {
    "ref/nagaraj_yao_region_map.sqlx",
    "stage/pat_family_forward_citations.sqlx",
    "stage/clinical_trial_core.sqlx",
    "int/pat_family_citation_quantile_flags.sqlx",
    "int/ct_country_quarter_measures.sqlx",
    "int/grant_country_quarter_measures.sqlx",
    "assertions/assert_quantile_distribution.sqlx",
    "assertions/assert_trial_bounds.sqlx",
    "assertions/assert_world_totals_monotone.sqlx",
    "assertions/assert_union3_bounds.sqlx",
}

APR16_MODIFIED = {
    "int/global_quarter_totals.sqlx",
    "int/pub_6way_decomp_ctq.sqlx",
    "int/pat_6way_fund_decomp_ctq.sqlx",
    "mart/panel_country_quarter_wide.sqlx",
}


def rel(p: Path) -> str:
    return str(p.relative_to(SRC)).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", help="Actually copy files")
    args = parser.parse_args()

    to_refresh = []
    to_skip = []
    for src in SRC.rglob("*.sqlx"):
        r = rel(src)
        if r in APR16_NEW or r in APR16_MODIFIED:
            to_skip.append(r)
            continue
        dst = DST / r
        if not dst.exists():
            to_refresh.append((src, dst, "NEW"))
        elif src.read_text() != dst.read_text():
            to_refresh.append((src, dst, "CHANGED"))

    if not to_refresh:
        print("Fork is up to date with Empirics (modulo apr16 new/modified files).")
        return 0

    print(f"{len(to_refresh)} files to refresh:")
    for src, dst, status in to_refresh:
        print(f"  [{status}] {rel(src)}")

    if args.apply:
        for src, dst, _ in to_refresh:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print(f"Copied {len(to_refresh)} files.")
    else:
        print("\nDry run. Re-run with --apply to copy files.")

    print(f"\nSkipped (apr16-owned): {len(to_skip)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

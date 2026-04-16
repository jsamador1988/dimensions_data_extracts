"""Regenerate all 9 figures in sequence. Fast; local-only (no BQ)."""

from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from pathlib import Path


FIGURE_MODULES = [
    "fig1_share_all",
    "fig2_share_uni",
    "fig3_share_gov",
    "fig4_share_grants",
    "fig5_share_trials",
    "fig6_us_pat_gov_and_direct",
    "fig7_us_pat_tiers",
    "fig8_pub_6way_usecn",
    "fig9_pat_6way_14c",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--figures", nargs="+", default=FIGURE_MODULES, help="Specific fig modules to run")
    parser.add_argument("--from-scratch", action="store_true", help="Delete outputs/figures first")
    args = parser.parse_args()

    here = Path(__file__).parent
    if args.from_scratch:
        import shutil
        figs_dir = here.parent / "outputs" / "figures"
        if figs_dir.exists():
            for f in figs_dir.iterdir():
                if f.is_file():
                    f.unlink()

    sys.path.insert(0, str(here))
    failures = []
    for mod_name in args.figures:
        print(f"\n=== {mod_name} ===")
        try:
            mod = importlib.import_module(mod_name)
            rc = mod.main()
            if rc != 0:
                failures.append((mod_name, rc))
        except Exception as e:  # noqa: BLE001
            print(f"  FAILED: {type(e).__name__}: {e}")
            failures.append((mod_name, str(e)))

    print("\n=== Summary ===")
    if failures:
        for m, r in failures:
            print(f"  FAIL  {m}  {r}")
        return 1
    print(f"  All {len(args.figures)} figures generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

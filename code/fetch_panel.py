"""Download the refreshed apr16 panel from BigQuery to data/panel_country_quarter_wide_apr16.csv.

Calls cost_estimator.checkpoint() before the fetch to enforce the $10 gate.
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import pandas as pd

from cost_estimator import checkpoint, estimate_query
from data_prep import load_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true", help="Skip interactive prompt after estimate")
    parser.add_argument("--threshold", type=float, default=None, help="Override $10 default")
    args = parser.parse_args()

    cfg = load_config()
    threshold = args.threshold if args.threshold is not None else cfg["cost"]["threshold_usd"]

    sql = f"""
    SELECT *
    FROM `{cfg['bq_project']}.{cfg['bq_dataset_mart']}.{cfg['bq_table_panel']}`
    WHERE quarter >= '{cfg['sample_start']}'
      AND quarter <= '{cfg['sample_end']}'
    """

    est = estimate_query(sql, label="fetch_panel")
    if not checkpoint("fetch_panel", [est], threshold_usd=threshold):
        return 2
    if not args.confirm:
        if input("Proceed with the fetch? [y/N] ").strip().lower() != "y":
            print("Aborted.")
            return 1

    print("Running query and downloading…")
    from google.cloud import bigquery
    client = bigquery.Client(project=cfg["bq_project"])
    df = client.query(sql).to_dataframe()

    out = Path(__file__).parent.parent / cfg["panel_csv"]
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows x {len(df.columns)} cols -> {out}")

    # Append actual-bytes to the cost ledger as a follow-up entry
    _log_actual("fetch_panel", df.memory_usage(index=False).sum() * 10)  # rough over-estimate
    return 0


def _log_actual(label: str, approx_bytes: int) -> None:
    log = Path(__file__).parent.parent / "logs" / "cost" / "cost_log.csv"
    with log.open("a") as f:
        f.write(f"{dt.datetime.now().isoformat()},{label}_actual,,,{approx_bytes},,\n")


if __name__ == "__main__":
    raise SystemExit(main())

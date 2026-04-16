"""Download the extended global_quarter_totals (apr16 version) from BigQuery."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cost_estimator import checkpoint, estimate_query
from data_prep import load_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--threshold", type=float, default=None)
    args = parser.parse_args()

    cfg = load_config()
    threshold = args.threshold if args.threshold is not None else cfg["cost"]["threshold_usd"]

    sql = f"""
    SELECT *
    FROM `{cfg['bq_project']}.{cfg['bq_dataset_int']}.{cfg['bq_table_world']}`
    WHERE quarter >= '{cfg['sample_start']}'
      AND quarter <= '{cfg['sample_end']}'
    ORDER BY quarter
    """

    est = estimate_query(sql, label="fetch_world_totals")
    if not checkpoint("fetch_world_totals", [est], threshold_usd=threshold):
        return 2
    if not args.confirm:
        if input("Proceed? [y/N] ").strip().lower() != "y":
            return 1

    from google.cloud import bigquery
    client = bigquery.Client(project=cfg["bq_project"])
    df = client.query(sql).to_dataframe()

    out = Path(__file__).parent.parent / cfg["world_totals_csv"]
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows x {len(df.columns)} cols -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

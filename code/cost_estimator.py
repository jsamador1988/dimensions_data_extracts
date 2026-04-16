"""BigQuery cost estimator with a hard threshold gate.

Usage:
    from cost_estimator import estimate_query, estimate_dataform, checkpoint

    est = estimate_query("SELECT COUNT(*) FROM `dimensions-ai.data_analytics.patents`")
    # {"bytes": 123456789, "mb": 117.7, "usd": 0.0006}

    checkpoint("label", [est1, est2], threshold_usd=10.0)
    # Prints summary, logs to data/cost_log.csv, raises SystemExit if total > threshold.

Matches the cost-estimation gate required by the data-pipeline-runner agent protocol
(see .claude/commands/data-pipeline-runner.md, Step 2 pre-flight-check).
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None  # Allow import-time success; we fail lazily at runtime.

_HERE = Path(__file__).parent
_ROOT = _HERE.parent  # paper_first_draft/
PRICE_PER_TB = 5.0  # BigQuery on-demand


@dataclass
class Estimate:
    label: str
    bytes_: int

    @property
    def mb(self) -> float:
        return self.bytes_ / 1024 / 1024

    @property
    def usd(self) -> float:
        return self.bytes_ / 1e12 * PRICE_PER_TB

    def to_dict(self) -> dict:
        return {"label": self.label, "bytes": self.bytes_, "mb": round(self.mb, 2), "usd": round(self.usd, 4)}


def estimate_query(sql: str, label: str = "", project: str = "dimensionsdataextracts") -> Estimate:
    if bigquery is None:
        raise RuntimeError("google-cloud-bigquery not installed. pip install google-cloud-bigquery")
    client = bigquery.Client(project=project)
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    q = client.query(sql, job_config=job_config)
    return Estimate(label=label or sql[:60].replace("\n", " "), bytes_=q.total_bytes_processed)


def estimate_dataform(compiled_graph_path: str | Path | None = None,
                      project: str = "dimensionsdataextracts") -> list[Estimate]:
    """Walk a Dataform compiled-graph JSON, dry-run each action's incremental-query,
    return a list of Estimates.  If compiled_graph_path is None, looks for the most
    recent snapshot under logs/dataform/compiled_graph_snapshots/.
    """
    if compiled_graph_path is None:
        snap_dir = _ROOT / "logs" / "dataform" / "compiled_graph_snapshots"
        snaps = sorted(snap_dir.glob("*.json"))
        if not snaps:
            raise FileNotFoundError(
                "No compiled_graph snapshot found. Run `cd paper_first_draft/dataform && "
                "dataform compile --json > ../logs/dataform/compiled_graph_snapshots/snap.json` first.")
        compiled_graph_path = snaps[-1]
    graph = json.loads(Path(compiled_graph_path).read_text())

    out: list[Estimate] = []
    for tbl in graph.get("tables", []):
        sql = tbl.get("incrementalQuery") or tbl.get("query")
        if not sql:
            continue
        name = f"{tbl['target']['schema']}.{tbl['target']['name']}"
        try:
            out.append(estimate_query(sql, label=name, project=project))
        except Exception as e:  # noqa: BLE001  best-effort per-action
            out.append(Estimate(label=f"{name} [DRY-RUN-FAILED: {type(e).__name__}]", bytes_=0))
    return out


def checkpoint(label: str, estimates: list[Estimate], threshold_usd: float = 10.0) -> bool:
    """Print a summary, log the checkpoint, and return True if total_usd <= threshold."""
    total_bytes = sum(e.bytes_ for e in estimates)
    total_usd = total_bytes / 1e12 * PRICE_PER_TB

    print(f"\n=== Cost checkpoint: {label} ===")
    print(f"  {'action':60s}  {'MB':>10s}  {'USD':>8s}")
    print(f"  {'-'*60}  {'-'*10}  {'-'*8}")
    for e in sorted(estimates, key=lambda x: -x.bytes_)[:30]:
        print(f"  {e.label[:60]:60s}  {e.mb:10.2f}  ${e.usd:7.4f}")
    if len(estimates) > 30:
        print(f"  ... and {len(estimates) - 30} more ...")
    print(f"  {'TOTAL':60s}  {total_bytes/1024/1024:10.2f}  ${total_usd:7.4f}")

    _log_checkpoint(label, estimates, total_bytes, total_usd)

    ok = total_usd <= threshold_usd
    if not ok:
        print(f"\n  !! TOTAL ${total_usd:.2f} EXCEEDS THRESHOLD ${threshold_usd:.2f} — stopping.")
    else:
        print(f"  OK: under ${threshold_usd:.2f} threshold.")
    return ok


def _log_checkpoint(label: str, estimates: list[Estimate], total_bytes: int, total_usd: float) -> None:
    log_dir = _ROOT / "logs" / "cost"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Full JSON snapshot
    (log_dir / f"cost_estimates_{ts}.json").write_text(
        json.dumps({"label": label, "total_bytes": total_bytes, "total_usd": total_usd,
                    "estimates": [e.to_dict() for e in estimates]}, indent=2)
    )

    # Append to running ledger
    ledger = log_dir / "cost_log.csv"
    is_new = not ledger.exists()
    with ledger.open("a", newline="") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["timestamp", "label", "est_bytes", "est_usd", "actual_bytes", "actual_usd", "delta_usd"])
        w.writerow([dt.datetime.now().isoformat(), label, total_bytes, round(total_usd, 4), "", "", ""])


if __name__ == "__main__":  # tiny smoke test
    import sys
    if len(sys.argv) > 1:
        est = estimate_query(Path(sys.argv[1]).read_text(), label=sys.argv[1])
        checkpoint(sys.argv[1], [est])
    else:
        print("Usage: python cost_estimator.py <path-to-sql-file>")

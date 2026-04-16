"""Loader for paper_first_draft canonical inputs.

Exposes:
  load_panel() -> DataFrame (country x quarter)
  load_world() -> DataFrame (quarter indexed)
  load_config() -> dict (config_apr16.yaml)

The panel is produced by fetch_panel.py (BigQuery fetch of rd_mart.panel_country_quarter_wide).
The world totals are produced by fetch_world_totals.py (BigQuery fetch of rd_int.global_quarter_totals).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

_HERE = Path(__file__).parent
_ROOT = _HERE.parent  # paper_first_draft/


def load_config() -> dict:
    with (_HERE / "config_apr16.yaml").open() as f:
        return yaml.safe_load(f)


def load_panel(cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or load_config()
    csv_path = _ROOT / cfg["panel_csv"]
    df = pd.read_csv(csv_path, parse_dates=["quarter"])
    return df


def load_world(cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or load_config()
    csv_path = _ROOT / cfg["world_totals_csv"]
    df = pd.read_csv(csv_path, parse_dates=["quarter"])
    return df

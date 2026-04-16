"""Nagaraj-Yao region aggregation utilities for paper_first_draft figures.

Exposes:
  REGIONS -- dict region_code -> list of ISO country codes
  classify(country_code) -> region_code or None
  annualize(df, year_col="quarter") -> df with "year" col (group-sum over calendar year)
  region_shares(panel_df, world_df, num_col, denom_col, year_range) ->
      DataFrame indexed by year with one column per region (US/EU/REST_HI/CHINA/REST_OF_WORLD),
      values = regional share of worldwide denominator

Fractional attribution is ALREADY baked into the panel's *_ctq columns (see
pub_pub_country_base and pat_family_country_base SQLX). The regional aggregator
just sums country-level numerators within the region; the worldwide denominator
is read straight from global_quarter_totals.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml


def _load_config() -> dict:
    cfg_path = Path(__file__).parent / "config_apr16.yaml"
    with cfg_path.open() as f:
        return yaml.safe_load(f)


_CFG = _load_config()
REGIONS: dict[str, list[str]] = _CFG["regions"]
REGION_ORDER: list[str] = _CFG["region_order"]
REGION_LABELS: dict[str, str] = _CFG["region_labels"]
REGION_COLORS: dict[str, str] = _CFG["region_colors"]


def classify(country_code: str) -> str | None:
    """Return the ny_region code for the country (US/EU/REST_HI/CHINA) or None.
    REST_OF_WORLD is computed residually, not assigned per-country here."""
    for region, countries in REGIONS.items():
        if country_code in countries:
            return region
    return None


def annualize(df: pd.DataFrame, year_col: str = "quarter") -> pd.DataFrame:
    """Resample a quarterly panel to annual by summing within calendar year.
    Assumes the quarter column is a string 'YYYY-MM-DD' or a date."""
    out = df.copy()
    out["year"] = pd.to_datetime(out[year_col]).dt.year
    return out


def region_shares(
    panel: pd.DataFrame,
    world: pd.DataFrame,
    num_col: str,
    denom_col: str,
    year_range: tuple[int, int],
) -> pd.DataFrame:
    """Compute (regional numerator) / (worldwide denominator) per year.

    Parameters
    ----------
    panel : country x quarter panel (paper_first_draft canonical)
    world : quarter-indexed world totals (global_quarter_totals export)
    num_col : column in panel to sum across countries in each region
    denom_col : column in world used as worldwide denominator
    year_range : inclusive (start_year, end_year)

    Returns
    -------
    DataFrame with year index and columns = REGION_ORDER (5 regions).
    REST_OF_WORLD is world_share - (US + EU + REST_HI + CHINA).
    """
    start_y, end_y = year_range

    # Tag each country with its region (None -> will be treated as residual)
    p = panel.copy()
    p["ny_region"] = p["country_code"].map(classify)
    p = annualize(p, "quarter")
    p = p[(p["year"] >= start_y) & (p["year"] <= end_y)]

    # Sum within (year, region) for rows with explicit region
    num_by_region = (
        p.dropna(subset=["ny_region"])
        .groupby(["year", "ny_region"])[num_col]
        .sum()
        .unstack("ny_region")
        .reindex(columns=["US", "EU", "REST_HI", "CHINA"], fill_value=0.0)
    )

    # Worldwide denominator per year
    w = world.copy()
    w["year"] = pd.to_datetime(w["quarter"]).dt.year
    denom_by_year = w[(w["year"] >= start_y) & (w["year"] <= end_y)].groupby("year")[denom_col].sum()

    # Shares per explicit region
    shares = num_by_region.div(denom_by_year, axis=0)

    # Rest-of-World residual
    shares["REST_OF_WORLD"] = 1.0 - shares[["US", "EU", "REST_HI", "CHINA"]].sum(axis=1)

    # Reorder columns and guard against small-negative residuals from float error
    shares = shares[REGION_ORDER]
    shares["REST_OF_WORLD"] = shares["REST_OF_WORLD"].clip(lower=0.0)

    return shares


def country_shares(
    panel: pd.DataFrame,
    world: pd.DataFrame,
    num_col: str,
    denom_col: str,
    year_range: tuple[int, int],
    countries: Iterable[str],
) -> pd.DataFrame:
    """Compute per-country (one line per country) share of the worldwide denominator.
    Used for Figures 8 and 9 when specific country sets are needed."""
    start_y, end_y = year_range

    p = annualize(panel[panel["country_code"].isin(list(countries))], "quarter")
    p = p[(p["year"] >= start_y) & (p["year"] <= end_y)]

    num = (
        p.groupby(["year", "country_code"])[num_col]
        .sum()
        .unstack("country_code")
        .reindex(columns=list(countries), fill_value=0.0)
    )

    w = world.copy()
    w["year"] = pd.to_datetime(w["quarter"]).dt.year
    denom_by_year = w[(w["year"] >= start_y) & (w["year"] <= end_y)].groupby("year")[denom_col].sum()

    return num.div(denom_by_year, axis=0).clip(lower=0.0)

# Grant Validation Export (Dimensions-only)

This update keeps grant validation fully inside Dimensions-based pipeline objects. OECD comparison is intentionally external.

## Output Table For Local Comparison

- `rd_mart.grant_dimensions_coverage_annual`

Granularity:
- `country_code`
- `year`
- `allocation_scenario` (`start_year`, `spread_3y`, `spread_5y`)

Key quantities included:
- Total grant USD by funder type (`gov`, `nongov`)
- Linked USD to patents/publications (any, patent-only, publication-only, both)
- Linked shares
- Grant counts
- USD also provided in million USD columns (`*_musd`)

## Deduplication Guarantee

Grant dollars are deduplicated at `country_code, grant_id` in:
- `rd_int.grant_domestic_unique`

All downstream linkage/coverage tables read from that deduped backbone, so grants linked to multiple patents/publications are counted once in `usd_linked_any_output`.

## Country Universe

Country universe is now maintained directly in:
- `rd_ref.analysis_country_map`

No OECD workbook table is required by these pipeline outputs.

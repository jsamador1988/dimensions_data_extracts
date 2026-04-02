# Dimensions Dataform Pipeline

BigQuery Dataform pipeline for extracting and transforming Dimensions patent, publication, grant, quality-filter, and science-linkage data into the live `apr_02` country-quarter panel.

## Live Workspace Layout

The canonical Dataform workspace is `Empirics/dataform`. After the assertion cleanup, the live repository contains 79 SQLX definition files:

- `ref/` (11): reference tables plus 4 declaration-backed external linkage sources
- `stage/` (25): raw extraction, weighting, grant flattening, and publication quality features
- `int/` (37): linkage ledgers, country-quarter aggregation, science linkage, and quality-filter measures
- `mart/` (2): final balanced panel outputs
- `assertions/` (4): live `apr_02` assertion suite

The compiled live graph should produce 75 actions: 71 datasets and 4 assertions. Assertions target the default assertion dataset `rd_assert` from `workflow_settings.yaml`.

## Live Assertion Suite

All live assertions belong in `definitions/assertions/`:

- `assert_private_citation_bounds.sqlx`
- `assert_component_bounds.sqlx`
- `assert_quality_filter_bounds.sqlx`
- `assert_uni_bounds.sqlx`

These assertions validate only columns defined by the current `apr_02` SQLX mart once that mart has been rebuilt. Historical `mar_17` whole-count and binary-citation assertions are intentionally not part of the live workspace.

## Historical `mar_17` Snapshot

The `data_description_pipeline/` directory preserves the historical `mar_17` whole-count and binary-citation extension. Its SQLX copies and assertions remain there for reproducibility of the data description report and should not be copied back into the live `Empirics/dataform` workspace without also restoring the underlying mart columns.

## Compile Workflow

Run from `Empirics/dataform`:

```bash
dataform compile
```

If the compile succeeds, the live assertion targets should all resolve under `rd_assert` and no action should target the legacy assertion dataset.

For a full run, make sure the manually uploaded declaration-backed BigQuery tables referenced in `definitions/ref/` exist before executing the graph.

## GCP Project

- Default project: `dimensionsdataextracts`
- Default dataset: `rd_stage`
- Default assertion dataset: `rd_assert`
- Location: `US`

## Key Design Patterns

- Fractional weighting: patents use inventor-country shares and publications use author-affiliation shares.
- Three-tier grant linkage: direct, researcher-ID, and institution-fuzzy matching.
- Surico classification: government funding organizations are classified from Dimensions types plus project curation.
- Quality-filter outputs: top-journal and breakthrough publication variants are materialized in the live `apr_02` graph.
- Historical isolation: experimental or report-specific extensions stay under their own reproduction folders unless their mart schema is restored end to end.

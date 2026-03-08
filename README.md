# Dimensions Dataform Pipeline

BigQuery Dataform pipeline for extracting and transforming Dimensions patent and publication data, linking to government funding, and producing country-quarter panels.

## Architecture

Four-layer pipeline (ref -> stage -> int -> mart):

### ref/ (3 files) - Reference tables
- `analysis_country_map.sqlx` - ISO country code mapping
- `gov_org_whitelist.sqlx` - Government organization whitelist
- `org_gov_surico.sqlx` - Surico-style government classification

### stage/ (24 files) - Raw extraction and flattening
Patent family construction, inventor/assignee weighting, publication author country attribution, grant flattening. Key patterns:
- Fractional country weighting (inventor-weighted for patents, author-weighted for publications)
- FoR4 (Fields of Research) classification
- Grant organization and researcher ID flattening

### int/ (28 files) - Linkage, aggregation, funding decomposition
Three-tier grant-to-output linkage:
1. **Direct** (Tier 1): Dimensions native grant-patent/publication links
2. **Researcher ID** (Tier 2): Same researcher appears on both grant and output
3. **Institution** (Tier 3): Same institution on grant and output, with concept/title Jaccard hardening

Funding decomposition into government-funded vs private for both patents and publications. Country-quarter aggregation of all measures.

### mart/ (2 files) - Final outputs
- `panel_country_quarter_wide.sqlx` - Wide panel with all patent/publication counts by funding type
- `grant_dimensions_coverage_annual.sqlx` - Grant coverage diagnostics

## GCP Project
- Default project: `dimensionsdataextracts`
- Default dataset: `rd_stage`
- Location: US

## Key Design Patterns
- **Fractional weighting**: Patents split across countries by inventor share; publications by author affiliation share
- **3-tier linkage**: Progressively looser grant-output matching with quality guardrails
- **Surico classification**: Government funding organizations classified per Surico et al. taxonomy
- **Configurable windows**: Sample dates, matching windows, and fuzzy thresholds set in `workflow_settings.yaml`

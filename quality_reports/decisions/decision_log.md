# paper_first_draft -- Decision Log

Chronological record of methodology decisions for the paper. Append-only. Each entry:

```
### YYYY-MM-DD HH:MM -- <short title>
- **Context**: why the decision was needed
- **Options considered**: alternative approaches
- **Decision**: what was chosen
- **Rationale**: why
- **Consequences**: downstream effects (code, data, analysis)
```

---

### 2026-04-16 -- Dataform pipeline approach: full self-contained fork
- **Context**: User's Plan Apr16.docx requires all files for the effort to live under `paper_first_draft/`, including updated Dataform.
- **Options considered**:
  (a) Additive sync pattern -- new/modified SQLX in paper_first_draft/dataform_additions/, sync into Empirics/dataform/ before run.
  (b) Full self-contained fork -- copy all 98 SQLX into paper_first_draft/dataform/.
  (c) Symlink hybrid -- shared SQLX symlinked from Empirics.
- **Decision**: (b) full fork.
- **Rationale**: User explicit preference (AskUserQuestion answer). Maximum self-containment; paper audit trail is entirely local to this folder.
- **Consequences**:
  - 92 SQLX duplicated from `Empirics/dataform/definitions/` into `paper_first_draft/dataform/definitions/`.
  - Schemas kept as rd_ref/rd_stage/rd_int/rd_mart/rd_assert (NOT renamed to *_apr16) -- the fork will overwrite production tables on run. Since new/modified SQLX are strict supersets of the Empirics versions (new columns, new tables), this is safe.
  - `sync_from_empirics.py` script provides a way to refresh the fork from Empirics upstream without clobbering apr16-owned files.

### 2026-04-16 -- Regional strategy: keep 36 countries + residual
- **Context**: Need to match Nagaraj/Yao's 5-region taxonomy (US, EU, Rest HI, China, Rest M/LI) but panel has only 36 countries; "Rest M/LI" implicitly covers ~12+ countries not in panel (IN, BR, RU, etc.).
- **Options considered**:
  (a) Add ~15 M/LI countries to the panel (BRICS + MENA + ASEAN).
  (b) Eliminate "Rest M/LI" as a category; compute "Rest of World" as residual from worldwide totals.
  (c) Minimal extension (BRICS + SG/TW).
- **Decision**: (b) residual approach (user refinement after initial Q preferred (a)).
- **Rationale**: Simpler, cheaper, and preserves the visual story. "Rest of World" is interpretable as "everything not explicitly tracked" and sums correctly because worldwide denominators are truly global.
- **Consequences**:
  - No new countries added to the panel.
  - `ref/nagaraj_yao_region_map.sqlx` stores only 4 regions (US, EU, REST_HI, CHINA).
  - `common_regions.py::region_shares` computes REST_OF_WORLD = 1 - sum(4 regions) per year.
  - Panel members not in any of the 4 regions (MX, TR, CO, CR) flow into the residual -- acceptable given these are not emphasized regions.
  - Saved estimated $3-5 in BQ cost by not materializing 10+ extra countries' full pipeline.

### 2026-04-16 -- Attribution: fractional throughout (vs. Nagaraj/Yao random selection)
- **Context**: Plan demands fractional attribution for multi-country items AND demands our Fig 1 top-left/top-right pubs match Nagaraj/Yao Fig 1b "exactly". N-Y use random-single-affiliation, which is incompatible with fractional.
- **Options considered**:
  (a) Fractional throughout; document the ~3-5pp gap in figure note.
  (b) Dual version: fractional + random-selection variant for Fig 1.
  (c) Random selection for Fig 1 only.
- **Decision**: (a) fractional throughout.
- **Rationale**: Internal consistency across all 9 figures is more important than exact N-Y match. The gap is documented and an overlay figure visualizes it.
- **Consequences**:
  - Fig 1 pubs panels will not exactly match N-Y published values; expect US share ~3-5pp higher under fractional (each US-affiliated paper is counted proportionally even when a co-author is foreign).
  - `outputs/validation/ny_fig1b_overlay.png` to be produced as a validation artifact comparing our series to N-Y's published values.
  - Paper figure 1 caption explicitly flags this attribution choice.

### 2026-04-16 -- Patent top-5%: IPC-4 x app-year x rep-doc jurisdiction x 5y window
- **Context**: Plan specifies "top 5% of forward citations normalized by tech class + grant year + jurisdiction" but leaves each dimension's operationalization open.
- **Options considered**:
  (a) IPC-4 x app-year x rep-doc jurisdiction x 5y window, family-level.
  (b) CPC subclass x grant-year x per-filing-jurisdiction x lifetime cites.
  (c) IPC-4 x app-year x jurisdiction x 3y window.
- **Decision**: (a).
- **Rationale**: Matches Fleming et al. (Science 2019) and Hall-Jaffe-Trajtenberg (NBER 2001) standards. 5y window avoids age bias. IPC-4 gives ~700 cells with enough per-cell N. Rep-doc jurisdiction is unambiguous (one per family). Application year anchors the forward-cite clock.
- **Consequences**:
  - `stage/pat_family_forward_citations.sqlx` computes `fwd_cites_5y` (and lifetime for reference).
  - `int/pat_family_citation_quantile_flags.sqlx` computes `is_top5c` via percent-rank within cell, with fallback to `(ipc4, app_year)` when cell <20 families.
  - `assert_quantile_distribution.sqlx` enforces [3%, 7%] top-5c share per year globally.

### 2026-04-16 -- Grants/trials attribution: research-org country
- **Context**: Fig 4 plan says "by where the research organization is located"; Fig 5 left open.
- **Decision**: Research-org country for both, fractional when multi-country.
- **Rationale**: Consistent with pubs/patents. Matches the "where the work is performed" semantic.
- **Consequences**:
  - `int/grant_country_quarter_measures` uses `grant_orgs_flat.country_code` (research orgs), not `funder_org.country_code`.
  - `int/ct_country_quarter_measures` uses `clinical_trial_core.research_org_countries` (from sponsor.country_code, fractional).

### 2026-04-16 -- Figure layouts: Fig 6 (1x2), Fig 7 (2x2), Fig 9 (patents, 14c)
- **Context**: Plan text had typos and ambiguous layouts.
- **Decisions**:
  - Fig 6 = 1x2 (gov-owned | private-with-direct-gov-link), both vs. total US patents.
  - Fig 7 = 2x2: RID-linked | INST-linked | (RID+INST)vs(direct) overlay | union-of-3-dedup.
  - Fig 9 = patents (typos about "publications" ignored); 14 countries = [AU, AT, BE, CA, CN, CZ, DE, IT, JP, PT, SI, CH, GB, US] (matches `pat_6way_fund` country_set in report_config_apr11.yaml).
- **Rationale**: User confirmed in AskUserQuestion round 2.

### 2026-04-16 -- Referee integration: spec file, not new subagent
- **Context**: User wanted a paper-specific referee "trained on" the Literature folder.
- **Options considered**:
  (a) New subagent at `paper_first_draft/.claude/agents/referee-econ.md`.
  (b) Spec file at `paper_first_draft/quality_reports/specs/` that extends the existing `/referee` agent.
- **Decision**: (b).
- **Rationale**: Existing `/referee` has mature machinery (P0-P4 severity, deliberative-review escalation, output contract). Adding a spec file is lighter and reuses institutional knowledge. Fewer moving parts.
- **Consequences**:
  - `quality_reports/specs/2026-04-16_paper_first_draft_spec.md` created with literature bindings and 7 review focus areas.
  - Invocation pattern: `/referee <spec-file> <stage>` at each of the 5 checkpoints.
  - Output convention: `paper_first_draft/quality_reports/referee/YYYY-MM-DD_<stage>.md`.

### 2026-04-16 -- Runtime isolation via schemaSuffix: "_apr16"
- **Context**: Filesystem self-containment (all 102 SQLX in paper_first_draft/dataform/) does not imply BigQuery dataset isolation. Each SQLX's `config { schema: "rd_int", ... }` block specifies the BQ dataset to write to; absent a suffix, the fork would materialize into the production datasets used by Empirics, overwriting production tables with our extended versions.
- **Options considered**:
  (a) Leave schemas as-is (rd_ref/rd_stage/rd_int/rd_mart/rd_assert). Safe because our modifications are strict supersets, but prevents A/B comparison.
  (b) Add `schemaSuffix: "_apr16"` to `workflow_settings.yaml`. Dataform auto-appends "_apr16" to every resolved schema at runtime; fork writes to rd_*_apr16 datasets, production untouched.
- **Decision**: (b).
- **Rationale**: Zero risk to production, allows A/B comparison of old vs. new panel, clearer audit trail. The only cost is doubled BQ storage while both pipelines coexist (cheap).
- **Consequences**:
  - `paper_first_draft/dataform/workflow_settings.yaml` gained `schemaSuffix: _apr16` with a comment explaining effect.
  - `paper_first_draft/code/config_apr16.yaml` bq_dataset_* values changed from `rd_*` to `rd_*_apr16` so fetch_panel.py / fetch_world_totals.py read from the suffixed datasets.
  - Internal `${ref("schema", "name")}` calls auto-resolve with the suffix (Dataform Core 3.x behavior) -- no SQLX edits needed.
  - External refs (`dimensions-ai.data_analytics.*`) unaffected -- they remain read-only source tables.
  - First run of the fork will materialize full copies of ref tables (gov_org_whitelist, org_gov_surico, analysis_country_map, etc.) into rd_ref_apr16. This adds ~10 MB of storage.

### 2026-04-16 -- Deferred: stage push of is_basic_pub
- **Context**: Plan's Dataform optimization #3 pushes `is_basic_pub` into `stage/pub_quality_features.sqlx` to drop a CROSS UNNEST in downstream consumers.
- **Decision**: Deferred. Risk of breaking existing 6-way decomp > savings at current cost levels.
- **Rationale**: Not a hot path (only one consumer). Savings measured in cents per run.
- **Consequences**: Optimization retained in plan notes for future revisit if costs climb.

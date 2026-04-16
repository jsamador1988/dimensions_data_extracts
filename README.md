# paper_first_draft -- Geography of Government-Funded Innovation (9 figures)

Paper in progress, extending Nagaraj & Yao (NBER w34694, 2026) "Geography of Science" and Surico et al. (NBER 2026) "Public Origins of American Innovation" to patents, grants, and clinical trials from 1980 to 2022.

## Quick links

- **Plan**: `C:/Users/jsam228/.claude/plans/carefully-read-the-outline-floating-cook.md` (or `quality_reports/plans/2026-04-16_plan_final.md` for local copy)
- **Figures**: `outputs/figures/fig{1..9}.{pdf,png,jpg}`
- **Paper**: `outputs/paper.tex` + `outputs/paper.pdf`
- **Referee spec**: `quality_reports/specs/2026-04-16_paper_first_draft_spec.md`
- **Decision log**: `quality_reports/decisions/decision_log.md`
- **Log directory key**: `logs/README.md`

## Directory layout

```
paper_first_draft/
  Plan Apr16.docx              user spec
  README.md                    this file
  dataform/                    fork of Empirics/dataform/ + 6 new + 5 modified + 4 new assertions
  code/                        14 python files (see below)
  data/                        downloaded panel + world totals + trials (CSV)
  outputs/
    figures/                   9 final figures (pdf/png/jpg)
    validation/                N-Y Fig 1b overlay, assertion outputs
    paper.tex, paper.pdf       compiled paper
  logs/                        raw execution logs (see logs/README.md)
  quality_reports/             structured quality artifacts (specs, plans, referee, verification, decisions, action_log, handoffs)
```

## Execution order

The plan has 10 stages. Each stage is executed through an existing agent or skill from `PF_Dimensions/.claude/`:

| Stage | Action | Agent / Skill | BQ cost |
|---|---|---|---|
| 0 | Scaffolding (this state) | `/checkin` + manual | $0 |
| 1 | BQ cost dry-run estimate | `/data-pipeline-runner` + `code/cost_estimator.py` | $0 (dry-run) |
| 2 | Materialize new stage tables | `/data-pipeline-runner` + `/run-pipeline` | ~$0.5-2 |
| 3 | Materialize int + mart (modified) | `/data-pipeline-runner` + `/merge-audit` + `/run-pipeline` | ~$2-6 |
| 3.5 | Panel consistency (Gate A) | `/verifier` + `/cross-file-check` | $0 |
| 3.6 | Research-design audit (Gate B) | `/research-design-auditor` | $0 |
| 4 | Download panel + world totals | `/data-pipeline-runner` + `fetch_panel.py`, `fetch_world_totals.py` | ~$0.1 |
| 5-8 | Generate Fig 1-3, 4-5, 6-7, 8-9 | direct + `/figure-style` + `/referee` per set | $0 |
| 9 | Compile paper.tex | `/compile-latex` | $0 |
| 9a | Full referee pass | `/referee` | $0 |
| 9b | Reproducibility (Gate E) | `/reproducibility-validator` | ~$0.1 |
| 9c | Pre-submission checklist | `/pre-submission` | $0 |
| End-of-session | Capture decisions, handoff | `/done` | $0 |

**Total expected BQ cost**: $3-8 on first full run; $0.2-1 on reruns. The `cost_estimator.checkpoint()` function halts any single step projected above $10.

## Python module manifest (code/)

| File | Role |
|---|---|
| `config_apr16.yaml` | Figure registry, regions, countries, paths, plot styles |
| `cost_estimator.py` | BQ dry-run + USD estimate + checkpoint gate |
| `sync_from_empirics.py` | Refresh fork from upstream Empirics (non-apr16 SQLX only) |
| `data_prep.py` | Load panel + world totals CSVs |
| `common_regions.py` | NY region aggregator + Rest-of-World residual |
| `plot_helpers.py` | Shared plotting primitives (grids, colors, save) |
| `fetch_panel.py` | BQ download of `rd_mart.panel_country_quarter_wide` |
| `fetch_world_totals.py` | BQ download of `rd_int.global_quarter_totals` |
| `fig1_share_all.py` | Figure 1 (2x3 pub+pat x all/basic/top5) |
| `fig2_share_uni.py` | Figure 2 (university-owned subset) |
| `fig3_share_gov.py` | Figure 3 (government-owned subset) |
| `fig4_share_grants.py` | Figure 4 (2x2 grants) |
| `fig5_share_trials.py` | Figure 5 (1x2 clinical trials) |
| `fig6_us_pat_gov_and_direct.py` | Figure 6 (1x2 US patents) |
| `fig7_us_pat_tiers.py` | Figure 7 (2x2 US 3-tier linkage) |
| `fig8_pub_6way_usecn.py` | Figure 8 (1x3 pubs US/EU/CN 2000-2022) |
| `fig9_pat_6way_14c.py` | Figure 9 (1x3 patents 14 countries 2000-2022) |
| `generate_all_figures.py` | Orchestrator: run all 9 in sequence |
| `generate_tex.py` | Assemble paper.tex; optional pdflatex compile |

## Dataform manifest (dataform/definitions/)

Forked from `Empirics/dataform/definitions/` (92 SQLX files) on 2026-04-16. Schemas (rd_ref, rd_stage, rd_int, rd_mart, rd_assert) unchanged -- fork writes to production datasets; additions are strict supersets.

**New files** (10):
- `ref/nagaraj_yao_region_map.sqlx`
- `stage/pat_family_forward_citations.sqlx`
- `stage/clinical_trial_core.sqlx`
- `int/pat_family_citation_quantile_flags.sqlx`
- `int/ct_country_quarter_measures.sqlx`
- `int/grant_country_quarter_measures.sqlx`
- `assertions/assert_quantile_distribution.sqlx`
- `assertions/assert_trial_bounds.sqlx`
- `assertions/assert_world_totals_monotone.sqlx`
- `assertions/assert_union3_bounds.sqlx`

**Modified files** (4):
- `int/global_quarter_totals.sqlx` (+9 columns for basic/top5c/grants/trials world totals)
- `int/pub_6way_decomp_ctq.sqlx` (+3 union-3 pass-through columns)
- `int/pat_6way_fund_decomp_ctq.sqlx` (+3 union-3 pass-through columns, +basic flag, +top5c flag)
- `mart/panel_country_quarter_wide.sqlx` (+12 columns from new int tables)

## Running the pipeline

### Stage 1: Cost dry-run (before any spend)
```
cd paper_first_draft/dataform
dataform compile --json > ../logs/dataform/compiled_graph_snapshots/$(date +%Y%m%d_%H%M%S).json
cd ../code
python cost_estimator.py   # or programmatic: cost_estimator.estimate_dataform()
```

### Stages 2-3: Materialize new/modified tables
Delegated to `/data-pipeline-runner` -- it will run `dataform run --tag <new-table-tag>` with pre/post validation.

### Stage 4: Download refreshed panel + world totals
```
cd paper_first_draft/code
python fetch_panel.py         # prompts for confirm after cost estimate
python fetch_world_totals.py  # same
```

### Stages 5-8: Figures
```
cd paper_first_draft/code
python generate_all_figures.py                           # all 9
python generate_all_figures.py --figures fig1_share_all  # specific
```

### Stage 9: Paper
```
cd paper_first_draft/code
python generate_tex.py --compile   # writes outputs/paper.tex and runs pdflatex
```

## Memory

The active project memory entry is at `C:/Users/jsam228/.claude/projects/C--Users-jsam228-Claude-Projects-PF-Dimensions/memory/project_paper_first_draft.md`. Indexed from `MEMORY.md` at the same directory.

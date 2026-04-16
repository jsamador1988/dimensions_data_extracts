# paper_first_draft/logs -- log directory key

All execution output (as opposed to structured quality artifacts) lives here. Logs are **append-only and timestamp-prefixed** -- never overwrite. Structured quality artifacts (plans, specs, referee reports, verification reports, action logs) live in `../quality_reports/`.

## Naming convention

`YYYY-MM-DD_HHMMSS_<stage>_<action>.<ext>`

Example: `2026-04-17_142301_dataform_int.log`

## Subdirectories

### `dataform/`
Per-run Dataform / BigQuery output. Written by `/data-pipeline-runner` during Stages 2-3.

- `YYYY-MM-DD_HHMMSS_dataform_stage.log` -- `dataform run --tag stage` output
- `YYYY-MM-DD_HHMMSS_dataform_int_mart.log` -- `dataform run --tag int --tag mart` output
- `YYYY-MM-DD_HHMMSS_dataform_full_refresh.log` -- full-refresh runs (rare)
- `compiled_graph_snapshots/YYYY-MM-DD_HHMMSS.json` -- `dataform compile --json` output; consumed by `cost_estimator.estimate_dataform()`

### `cost/`
BQ cost tracking. Written by `code/cost_estimator.py`.

- `cost_log.csv` -- running ledger: timestamp, label, est_bytes, est_usd, actual_bytes, actual_usd, delta_usd
- `cost_estimates_YYYYMMDD_HHMMSS.json` -- full dry-run JSON per checkpoint
- `cost_summary.md` -- human-readable cumulative summary, regenerated after each session

### `downloads/`
Per-fetch logs. Written by `code/fetch_panel.py`, `code/fetch_world_totals.py`.

- `YYYY-MM-DD_HHMMSS_panel_fetch.log`
- `YYYY-MM-DD_HHMMSS_worldtotals_fetch.log`
- `YYYY-MM-DD_HHMMSS_clinical_trials_fetch.log` (if direct standalone pulls are needed)

### `figure_generation/`
Per-figure generator stdout + warnings. Written by each `fig*.py` during Stages 5-8.

- `YYYY-MM-DD_HHMMSS_fig<N>.log`
- `figure_generation_summary.md` -- one-line-per-figure pass/fail table, updated after `generate_all_figures.py`

### `tex_compile/`
LaTeX compilation output. Written by `/compile-latex` during Stage 9.

- `YYYY-MM-DD_HHMMSS_paper_tex.log`
- `paper_pdflatex_errors.md` -- recurring issues with fixes applied, if any

### `session/`
Full console transcripts for automated sessions (useful for post-hoc audit).

- `YYYY-MM-DD_HHMMSS_session.log`

## Relationship to `quality_reports/`

| Artifact type | Location |
|---|---|
| Raw BQ/CLI output, large text blobs | `logs/` (this directory) |
| Structured audit artifacts (specs, plans, referee reports) | `quality_reports/` |
| Per-session handoff (what next session needs) | `quality_reports/handoffs/` |
| Cumulative action log | `quality_reports/action_log.md` (paper-scoped) and top-level `PF_Dimensions/quality_reports/action_log.md` |

## Hygiene

- Logs are never deleted. If the directory grows too large, archive older than 90 days to `logs/archive/YYYY-MM/`.
- The `cost_log.csv` is the only file that should grow unboundedly -- if it does, `/done` at session end can rotate it to `cost_log_YYYY-MM.csv` and start fresh.

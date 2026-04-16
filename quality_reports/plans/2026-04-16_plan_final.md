# Paper First Draft — 9 Figures on Government-Funded Innovation (Revised Plan)

## Context

The user wrote a spec at `paper_first_draft/Plan Apr16.docx` for the final figures of an economics paper building on Nagaraj & Yao "The Geography of Science" (NBER w34694, Jan 2026) and Surico et al. "Public Origins of American Innovation" (NBER Jan 2026). The paper documents how much of global research output (publications, patents, grants, clinical trials) is publicly funded, broken down by ownership and quality tier, with special focus on US privately-owned patents plausibly linkable to US government funding.

Most of the infrastructure already exists:
- **Canonical panel**: `Empirics/data/raw/panel_country_quarter_wide_apr_11.csv` (11,701 rows × 159 cols × 36 countries, quarterly, sample_start 1980 per `report_config_apr11.yaml`)
- **Latest report**: `geography_gov_innovation_paper/outputs/gov_innovation_slides_apr14.tex` + `gov_innovation_report_apr14.pdf` produced Apr 16 — already has country/region-share-of-world figures for pubs and patents (2000-2024, 5 quality tiers) and 6-way / 8-way decompositions
- **Dataform pipeline** (98 SQLX at `Empirics/dataform/definitions/`): produces the panel plus `rd_int.global_quarter_totals` (pat+pub world totals with top5j/top01 flags), 3-tier gov-funding linkage (`pat_govfund_{direct,rid,inst}_fc`, `pub_govfund_{direct,rid,inst}_pc`) with UNION DISTINCT deduplication, basic-research FoR map, journal quality ranking, breakthrough flags, and 392-org government whitelist
- **Existing agents** (`.claude/commands/`): `/coordinator`, `/data-pipeline-runner`, `/diagnostics-runner`, `/verifier`, `/referee`, `/reproducibility-validator`, `/research-design-auditor`
- **Existing skills** (`.claude/skills/`): `/checkin`, `/done`, `/goals-review`, `/run-pipeline`, `/cross-file-check`, `/merge-audit`, `/compile-latex`, `/figure-style`, `/pre-submission`, `/replication-package-builder`
- **Existing conventions**: `quality_reports/{specs,plans,handoffs,referee,verification}/`, `quality_reports/action_log.md`, `~/.claude/handoff.md`, `AGENTS.md` quality gates A-F, P0-P4 severity taxonomy

The new work is: **(i)** fork the Dataform pipeline into `paper_first_draft/` for full self-containment, **(ii)** add 4 missing data pieces (patent forward-citation top-5%, clinical trials extraction, worldwide grant/trial totals, explicit union-of-3-tiers columns), **(iii)** extend figure generators to 1980-2022 with Nagaraj/Yao's 5-region scheme (US / EU / Rest HI / China / Rest of World computed as residual), **(iv)** register paper-scoped literature bindings for the existing `/referee` agent, **(v)** add cost-estimation gates before every BQ operation, **(vi)** route all execution through the existing agent/skill catalog so quality gates A-F are automatically enforced.

The user's resolved decisions (from AskUserQuestion rounds):
- **Dataform**: full self-contained fork inside `paper_first_draft/dataform/`
- **Panel countries**: keep the existing 36 countries — do NOT extend. Rest-of-World = `world_total − (US + EU + Rest HI + China)` using the worldwide denominators (replaces "Rest of M/LI")
- **Attribution**: fractional throughout (document the ~3-5pp gap vs. Nagaraj/Yao's random-affiliation method)
- **Patent top-5%**: IPC-4 × family-app-year × rep-doc jurisdiction cell, 5-year forward-cite window, family-level flag
- **Grants & trials**: attribute by research-organization country (not funder country), fractional when multi-country
- **US patent denominators (Fig 6/7)**: total US patents for both figures
- **Fig 6**: 1×2 (gov-owned share | privately-owned-direct-gov-link share)
- **Fig 7**: 2×2 — top: RID-linked | INST-linked — bottom-left: line overlay of `{RID∪INST}` vs. direct-link (validation) — bottom-right: `direct∪RID∪INST` de-duplicated
- **Fig 9**: patents (plan typos about "publications" ignored), 14 countries = `[AU, AT, BE, CA, CN, CZ, DE, IT, JP, PT, SI, CH, GB, US]`

## Integration with Existing Agents & Skills

Every stage of this plan is executed through an existing agent or skill — no stage operates outside the quality-gate machinery already in `AGENTS.md`. One new artifact is a **paper-scoped spec file** that the existing `/referee` agent picks up as part of its scope when asked to review this paper; no new subagent is needed.

| Stage | Work | Agent / Skill | Why |
|-------|------|---------------|-----|
| 0. Scaffolding | Create folder, copy Dataform, seed Python skeletons | (manual) + `/checkin` at session start | `/checkin` reads handoff.md and surfaces open P0-P1 issues before work begins |
| 1. BQ cost dry-run | Enumerate Dataform actions and dry-run each | `/data-pipeline-runner` invoking `code/cost_estimator.py` | Pre-flight-check step already required by `data-pipeline-runner` protocol |
| 2. Dataform stage materialization | Run new stage SQLX (forward-cites, clinical trials) | `/data-pipeline-runner` + `/run-pipeline` skill | run-pipeline is its executor; data-pipeline-runner enforces pre/post validation |
| 3. Dataform int/mart materialization | Run new int + modified mart | `/data-pipeline-runner` + `/merge-audit` skill + `/run-pipeline` | merge-audit is invoked on every new LEFT JOIN in the modified `panel_country_quarter_wide.sqlx` per existing `data-pipeline-runner` protocol |
| 3.5 Panel consistency check | Verify panel columns, row counts, monotone bounds | `/verifier` + `/cross-file-check` skill | `cross-file-check` verifies SQLX/Python/CSV/LaTeX consistency — used to confirm that the 9 new assertion files compile, the 12 new panel columns match `config_apr16.yaml`, and the N-Y region map is internally consistent |
| 3.6 Research-design audit | Audit patent top-5% spec, basic-research FoR rollup, union-3 logic, trial gov classification | `/research-design-auditor` | `research-design-auditor` is chartered for "LP identification, tier system, university definitions, grant linkage" — extending it to audit quality-tier definitions is a natural scope match |
| 4. Data download | Pull refreshed panel + world totals + clinical trials | `/data-pipeline-runner` invoking `fetch_panel.py` + `fetch_world_totals.py` | Same agent used for all BQ reads |
| 5-8. Figure generation | Generate Fig 1-3, 4-5, 6-7, 8-9 | (claude-code directly, using `plot_helpers.py`) + `/figure-style` skill after each set | `figure-style` validates visual consistency (axis labels, color scheme, DPI) — invoked once per figure set |
| 5a-8a. Referee checkpoints | Review each figure set against literature | `/referee` (reading the paper-scoped spec) | Existing `/referee` with new scope file loaded — see below |
| 9. Paper compile | pdflatex paper.tex | `/compile-latex` skill | Existing skill with error detection |
| 9a. Full referee pass | Review complete paper | `/referee` | Final review before shipping |
| 9b. Reproducibility check | Re-run end-to-end from CSVs | `/reproducibility-validator` | Gate E enforcement |
| 9c. Pre-submission | Final checklist | `/pre-submission` skill | Existing gate-F workflow |
| 9d. Replication package | Assemble shareable bundle | `/replication-package-builder` skill | Optional; for journal submission handoff |
| End of each session | Capture decisions, write handoff | `/done` skill | Logs to `quality_reports/action_log.md` and overwrites `~/.claude/handoff.md` |

### Referee scope extension (no new subagent)

Instead of creating a `referee-econ` subagent, extend the existing `/referee` by writing a **paper-scoped spec** at `paper_first_draft/quality_reports/specs/2026-04-16_paper_first_draft_spec.md`. When the user (or `/coordinator`) invokes `/referee`, it reads its "First Actions Every Session" (CLAUDE.md → AGENTS.md → prior reports) PLUS this spec, which binds the literature and review focus for this paper. Contents:

```
# Spec: paper_first_draft (Geography of Gov Innovation)

## Literature bindings (read in full before reviewing)
- Empirics/Literature/w34694 (1).pdf — Nagaraj & Yao "Geography of Science" (NBER 2026)
- Empirics/Literature/Public_innovation_Surico.pdf — Surico et al. "Public Origins" (NBER 2026)
- Empirics/Literature/science.aaw2373.pdf + aaw2373_fleming_sm.pdf — Fleming et al. (Science 2019)

## Paper scope
Nine figures in paper_first_draft/outputs/figures/ fig1..fig9.pdf; paper.tex compiled from them.

## Review focus (in addition to AGENTS.md gates A-F)
1. Fractional attribution vs. Nagaraj/Yao random-selection — is the ~3-5pp gap disclosed in the figure note?
2. Top-5% patent quantile — IPC-4 / app-year / rep-doc jurisdiction / 5-year window consistency with Fleming, Hall-Jaffe-Trajtenberg standards
3. Basic-research FoR rollup (FoR4 → FoR2 via SUBSTR) — defensible vs. OECD Frascati definitions
4. Union-3 de-duplication — validation overlay in Fig 7 bottom-left interpretable
5. NY region mapping — country-list explicit and time-invariant; Rest-of-World residual algebra sound
6. Clinical-trial gov classification — sponsor-based vs. funder-based choice defensible
7. Surico et al. concordance — our gov-owned vs. private-govfund vs. private-nongovfund buckets map cleanly to their three categories

## Deliverable paths reviewed
- paper_first_draft/outputs/figures/fig{1..9}.pdf
- paper_first_draft/outputs/paper.pdf
- paper_first_draft/data/panel_country_quarter_wide_apr16.csv
- paper_first_draft/data/world_quarter_totals_apr16.csv
- paper_first_draft/dataform/definitions/**/*.sqlx (new and modified only)
- paper_first_draft/code/*.py

## Output path
paper_first_draft/quality_reports/referee/YYYY-MM-DD_<stage>.md
```

This spec is read by the existing `/referee` and inherits all its machinery: severity P0-P4, ship/revise/major-redesign verdicts, deliberative-review for high-stakes passes, output contract to `quality_reports/referee/`.

## Folder Structure

All new files under `paper_first_draft/`. Existing `Empirics/dataform/` stays untouched as the project's canonical production pipeline.

```
paper_first_draft/
  Plan Apr16.docx                        (existing; user's spec)
  PLAN.md                                (this plan, copied into paper_first_draft/quality_reports/plans/ for persistence)
  README.md                              (run-book: how to execute each stage)
  dataform/                              (full fork of Empirics/dataform/)
    workflow_settings.yaml               (copied; defaultDataset bumped to rd_*_apr16 so forked runs do not overwrite production)
    .df-credentials.json                 (copied from Empirics; gitignored)
    definitions/
      ref/                               (7 copied + 1 new: nagaraj_yao_region_map)
      stage/                             (18 copied + 2 new: pat_family_forward_citations, clinical_trial_core; 1 modified: pub_quality_features)
      int/                               (44 copied + 3 new; 3 modified)
      mart/                              (1 copied + modified panel_country_quarter_wide)
      assertions/                        (5 copied + 4 new)
  code/
    config_apr16.yaml                    (figure registry, NY regions, 14-country Fig 9 list, quality thresholds)
    cost_estimator.py                    (BQ dry-run, bytes→USD, $10 threshold gate)
    sync_from_empirics.py                (one-shot: copy Empirics SQLX into paper_first_draft/dataform/, prints diff)
    fetch_panel.py                       (downloads refreshed mart panel from BQ)
    fetch_world_totals.py                (downloads refreshed global_quarter_totals; extended cols)
    data_prep.py                         (loads panel + world totals, annualizes, regional aggregation, Rest-of-World residual)
    common_regions.py                    (NY region map, EU membership list, fractional-attribution helpers)
    plot_helpers.py                      (2×3 / 2×2 / 1×3 / 1×2 grid layouts, shared styles)
    fig1_share_all.py .. fig9_pat_6way_14c.py   (9 figure generators)
    generate_all_figures.py              (orchestrator)
    generate_tex.py                      (builds paper.tex referencing figures)
  data/
    panel_country_quarter_wide_apr16.csv (refreshed, ~171 cols)
    world_quarter_totals_apr16.csv       (superset: pub_*, pat_*, grant_*, trial_* × {total, basic, top5, top01, gov})
    clinical_trials_country_quarter_apr16.csv (standalone for offline runs)
  outputs/
    figures/                             (fig1..fig9 .pdf + .png + .jpg)
    validation/                          (N-Y Fig 1b overlay, assertion output)
    paper.tex
    paper.pdf
  logs/                                  (see Logs section below)
  quality_reports/                       (paper-scoped; mirrors top-level conventions)
    action_log.md                        (paper-scoped action log; top-level action_log.md keeps project-wide entries)
    specs/
      2026-04-16_paper_first_draft_spec.md   (referee binding spec, above)
    plans/
      2026-04-16_plan_final.md           (copy of this plan)
    handoffs/
      YYYY-MM-DD_session_handoff.md
    referee/
      YYYY-MM-DD_fig1-3.md
      YYYY-MM-DD_fig4-5.md
      YYYY-MM-DD_fig6-7.md
      YYYY-MM-DD_fig8-9.md
      YYYY-MM-DD_paper_full.md
    verification/
      YYYY-MM-DD_panel_consistency.md
      YYYY-MM-DD_dataform_run_<tag>.md
      YYYY-MM-DD_reproducibility.md
    decisions/
      decision_log.md                    (chronological record of methodology choices)
```

## Dataform Additions & Modifications

Same as previously specified — summarized here. Each line lists the file and its purpose.

### New SQLX
1. **`ref/nagaraj_yao_region_map.sqlx`** — `(country_code, ny_region)`. `ny_region ∈ {US, EU, REST_HI, CHINA}`. EU = `[AT, BE, CH, CZ, DE, DK, EE, ES, FI, FR, GB, GR, HU, IE, IS, IT, LT, LU, LV, NL, NO, PL, PT, SE, SI, SK]` (EU-27 + UK + EFTA, panel intersection). Rest-HI = `[JP, KR, CA, AU, IL, NZ, CL]`. Unassigned panel members (MX, TR, CO, CR) flow into Rest-of-World residual.
2. **`stage/pat_family_forward_citations.sqlx`** — per-family forward-cite count (`fwd_cites_5y`, `fwd_cites_lifetime`), `anchor_jurisdiction`, `anchor_ipc4`. Partitioned by `family_app_qtr`, clustered by `(anchor_jurisdiction, anchor_ipc4)`.
3. **`int/pat_family_citation_quantile_flags.sqlx`** — percent-rank within `(anchor_ipc4, family_app_year, anchor_jurisdiction)`; sets `is_top5c`. Fallback to `(anchor_ipc4, family_app_year)` for <20-family cells. Incremental model with 8-quarter lookback.
4. **`stage/clinical_trial_core.sqlx`** — extract `dimensions-ai.data_analytics.clinical_trials`. Output: `trial_id, trial_qtr, sponsor_orgs, funder_orgs, research_org_countries, is_gov_sponsor`. Filter to trials with ≥1 country.
5. **`int/ct_country_quarter_measures.sqlx`** — fractional `{trial_total_ctq, trial_gov_ctq, trial_basic_ctq}` by country × quarter.
6. **`int/grant_country_quarter_measures.sqlx`** — `{grant_total_ctq, grant_basic_ctq, grant_gov_funder_ctq, grant_nongov_funder_ctq}`. Research-org country attribution.

### Modified SQLX
7. **`int/global_quarter_totals.sqlx`** — add 9 columns: `pat_world_top5c`, `pat_world_basic`, `pub_world_basic`, `grant_world_{total, basic, gov_funder, nongov_funder}`, `trial_world_{total, gov, basic}`. Partitioned by `quarter`.
8. **`int/pub_6way_decomp_ctq.sqlx`** — add 3 union-3 pass-through cols: `pub_union3_govfund_{, basic, top5j}_ctq`.
9. **`int/pat_6way_fund_decomp_ctq.sqlx`** — add 3 union-3 pass-through cols: `pat_union3_govfund_{, basic, top5c}_ctq`.
10. **`mart/panel_country_quarter_wide.sqlx`** — LEFT JOIN new tables; add ~12 columns (159 → ~171).
11. **`stage/pub_quality_features.sqlx`** — push `is_basic_pub` into stage (optimization).

### New Assertions
- `assert_quantile_distribution.sqlx` — global `is_top5c` share within any year ∈ [3%, 7%]
- `assert_trial_bounds.sqlx` — `trial_gov_ctq ≤ trial_total_ctq` per row
- `assert_world_totals_monotone.sqlx` — `*_basic ≤ *_total` for all four domains
- `assert_union3_bounds.sqlx` — union-3 cols bounded above by private+uni totals, below by direct-only

## Python Figure Generators

Colors in `plot_helpers.py`: US `#1f77b4`, EU `#8c564b`, Rest HI `#2ca02c`, China `#d62728`, Rest of World `#7f7f7f`.

| Fig | Script | Shape | Year range | Key columns |
|-----|--------|-------|-----------|-------------|
| 1 | `fig1_share_all.py` | 2×3 | 1980-2022 | 3 pub cols + 3 pat cols / world totals |
| 2 | `fig2_share_uni.py` | 2×3 | 1980-2022 | university-owned subsets |
| 3 | `fig3_share_gov.py` | 2×3 | 1980-2022 | government-owned subsets |
| 4 | `fig4_share_grants.py` | 2×2 | 1980-2022 | grant_{total, basic, gov_funder, nongov_funder}_ctq |
| 5 | `fig5_share_trials.py` | 1×2 | 1980-2022 | trial_{total, gov}_ctq |
| 6 | `fig6_us_pat_gov_and_direct.py` | 1×2 | 1980-2022 | US-only; pat_gov_owned_ctq, pat_govfund_direct_ctq (private subset) |
| 7 | `fig7_us_pat_tiers.py` | 2×2 | 1980-2022 | US; RID-only / INST-only / (RID∪INST vs. direct overlay) / union-of-3 |
| 8 | `fig8_pub_6way_usecn.py` | 1×3 | 2000-2022 | US/EU/CN × (all / top5j / basic) pub_union3_govfund |
| 9 | `fig9_pat_6way_14c.py` | 1×3 | 2000-2022 | 14 countries × (all / top5c / basic) pat_union3_govfund |

## Dataform Optimization (non-breaking)
1. Partition + cluster the new int/stage tables as listed above.
2. Push `is_basic_pub` into `stage/pub_quality_features` — drops a CROSS UNNEST in each 6-way decomp consumer.
3. Incremental `pat_family_citation_quantile_flags` with 8-quarter lookback.
4. Do NOT touch `pat_govfund_inst_fc` fuzzy-matching hot path (regression risk > savings at current cost levels).

## Cost Tracking

`code/cost_estimator.py` exports `estimate_query`, `estimate_dataform`, and `checkpoint(label, estimates, threshold_usd=10.0)`. Every fetch script and Dataform invocation calls the checkpoint first. Logs to `paper_first_draft/logs/cost/cost_log.csv` (timestamp, action, est_bytes, est_usd, actual_bytes).

## Logs Organization

All logs scoped to this paper live under `paper_first_draft/logs/` (execution artifacts) and `paper_first_draft/quality_reports/` (quality artifacts, mirroring top-level conventions). Naming convention: `YYYY-MM-DD_HHMMSS_<stage>_<action>.<ext>`.

```
paper_first_draft/logs/
  README.md                                           log directory key
  dataform/
    2026-MM-DD_HHMMSS_dataform_stage.log              per-run BQ/Dataform output
    2026-MM-DD_HHMMSS_dataform_int_mart.log
    2026-MM-DD_HHMMSS_dataform_full_refresh.log
    compiled_graph_snapshots/
      2026-MM-DD_HHMMSS.json                          dataform compile output snapshot
  cost/
    cost_log.csv                                      running ledger (timestamp, action, est_bytes, est_usd, actual_bytes, delta)
    cost_estimates_YYYYMMDD_HHMMSS.json               per-checkpoint full dry-run JSON
    cost_summary.md                                   human-readable cumulative summary, updated after each run
  downloads/
    YYYY-MM-DD_HHMMSS_panel_fetch.log
    YYYY-MM-DD_HHMMSS_worldtotals_fetch.log
    YYYY-MM-DD_HHMMSS_clinical_trials_fetch.log
  figure_generation/
    YYYY-MM-DD_HHMMSS_fig<N>.log                      per-figure stdout + warnings
    figure_generation_summary.md                      one-line-per-figure pass/fail table
  tex_compile/
    YYYY-MM-DD_HHMMSS_paper_tex.log
    paper_pdflatex_errors.md                          recurring issues, if any
  session/
    YYYY-MM-DD_HHMMSS_session.log                     full console transcript of automated runs
```

Logs are append-only and never overwrite prior entries. A short `logs/README.md` explains the naming convention and which skill/agent writes to which subdir, so any future reader (or `/checkin`) can navigate without guessing.

Complementing `logs/` (raw execution output), `quality_reports/` carries the structured quality artifacts:

```
paper_first_draft/quality_reports/
  action_log.md                                       paper-scoped action log (same format as top-level)
  specs/2026-04-16_paper_first_draft_spec.md          referee literature-binding spec
  plans/2026-04-16_plan_final.md                      this plan copy
  handoffs/YYYY-MM-DD_session_handoff.md              per-session handoff (copy of ~/.claude/handoff.md)
  referee/YYYY-MM-DD_<stage>.md                       referee reports (5 planned)
  verification/YYYY-MM-DD_<tag>.md                    verifier + reproducibility reports
  decisions/decision_log.md                           chronological methodology decisions
```

Entry points:
- Top-level `quality_reports/action_log.md` gets a single entry per session pointing to `paper_first_draft/quality_reports/action_log.md` for detail, preserving the project-wide audit trail.
- Each `/done` session writes a handoff to both `~/.claude/handoff.md` (global, next-session) and `paper_first_draft/quality_reports/handoffs/` (archival).

## Memory Organization

Memory lives at `C:\Users\jsam228\.claude\projects\C--Users-jsam228-Claude-Projects-PF-Dimensions\memory\`. Clearly label the new entry and keep the index concise.

**New memory file**: `memory/project_paper_first_draft.md`
```
---
name: Paper First Draft (Geography of Gov Innovation, 9 figures)
description: Active paper build in paper_first_draft/ — 9 figures, Nagaraj/Yao + Surico literature, self-contained Dataform fork, existing /referee agent with paper-scoped spec
type: project
---

**Active since**: 2026-04-16
**Plan**: C:\Users\jsam228\.claude\plans\carefully-read-the-outline-floating-cook.md (also at paper_first_draft/quality_reports/plans/)

**Key decisions (locked at plan approval)**
- Full Dataform fork in paper_first_draft/dataform/ (datasets bumped to rd_*_apr16)
- Panel stays at 36 countries; Rest-of-World = world - (US + EU + Rest HI + CN) via residual
- Fractional attribution throughout; ~3-5pp gap vs. N-Y documented in figure note
- Patent top-5% = IPC-4 × app-year × rep-doc jurisdiction × 5y fwd-cite
- Grants/trials by research-org country
- Fig 6 = 1x2; Fig 7 = 2x2 with RID/INST/overlay/union-3; Fig 9 = patents (not pubs), 14 countries = [AU, AT, BE, CA, CN, CZ, DE, IT, JP, PT, SI, CH, GB, US]

**Execution state**: Plan approved YYYY-MM-DD; Stage 0 scaffolding complete; next = Stage 1 cost estimate (/data-pipeline-runner)

**Open items**: (populated as execution progresses)

**Why it matters**: Surico et al.'s "Public Origins of American Innovation" + Nagaraj/Yao's 2026 NBER paper motivate a descriptive paper quantifying the global footprint of publicly-funded science. These 9 figures are the paper's empirical backbone; all subsequent estimation stages depend on these definitions.

**How to apply**: When user references "the paper", "the draft", or "paper_first_draft", check this memory file first, then plan file, then paper_first_draft/quality_reports/action_log.md.
```

**MEMORY.md index entry** (one-line, under ~150 chars):
```
- [Paper First Draft (9 figures)](project_paper_first_draft.md) — active 2026-04-16; self-contained Dataform fork; N-Y + Surico literature
```

Updated progressively: after each stage, append the stage outcome to the "Execution state" line; on session end, `/done` writes a summary into `paper_first_draft/quality_reports/action_log.md` and updates both the memory file and `MEMORY.md`.

## Execution Order (Staged with User Checkpoints)

| Stage | Action | Agent / Skill | BQ | Est. cost | Gate |
|-------|--------|---------------|----|-----------| ----|
| 0 | `/checkin`; scaffold folder, copy 98 SQLX, add new SQLX, write Python skeletons, write spec file, create logs/ and quality_reports/ | `/checkin`, then manual | No | $0 | User reviews structure vs. plan |
| 1 | `cost_estimator.estimate_dataform(tag="int", full_refresh=True)` on forked project | `/data-pipeline-runner` | Dry-run | $0 | User approves aggregate estimate |
| 2 | `dataform run --tag stage` (new stage tables only) | `/data-pipeline-runner` + `/run-pipeline` | Yes | ~$0.5-2 | Row-count + assertions pass |
| 3 | `dataform run --tag int --tag mart` | `/data-pipeline-runner` + `/run-pipeline` + `/merge-audit` | Yes | ~$2-6 | 9 assertions pass |
| 3.5 | Panel consistency, cross-file check | `/verifier` + `/cross-file-check` | No | $0 | Gate A pass |
| 3.6 | Research-design audit of new definitions | `/research-design-auditor` | No | $0 | Gate B pass |
| 4 | Fetch panel + world totals + clinical trials | `/data-pipeline-runner` | Minimal | ~$0.1 | Shape matches config_apr16.yaml |
| 5 | Generate Fig 1-3 | (direct) + `/figure-style` skill | No | $0 | Gate F pass; proceed to 5a |
| 5a | Referee Fig 1-3 (including N-Y Fig 1b overlay) | `/referee` (with paper-scoped spec) | No | $0 | Verdict SHIP or REVISE ≤ 2 rounds |
| 6 | Generate Fig 4-5 | (direct) + `/figure-style` | No | $0 | |
| 6a | Referee Fig 4-5 | `/referee` | No | $0 | |
| 7 | Generate Fig 6-7 | (direct) + `/figure-style` | No | $0 | |
| 7a | Referee Fig 6-7 | `/referee` | No | $0 | |
| 8 | Generate Fig 8-9 | (direct) + `/figure-style` | No | $0 | |
| 8a | Referee Fig 8-9 | `/referee` | No | $0 | |
| 9 | Compile `paper.tex` | `/compile-latex` | No | $0 | Gate F pass |
| 9a | Full referee pass on paper.pdf | `/referee` | No | $0 | |
| 9b | End-to-end reproducibility check | `/reproducibility-validator` | Minimal | ~$0.1 | Gate E pass |
| 9c | Pre-submission checklist | `/pre-submission` | No | $0 | All gates pass |
| 9d | (Optional) Assemble replication bundle | `/replication-package-builder` | No | $0 | |
| End of session | Capture decisions, write handoff | `/done` | No | $0 | action_log + handoff updated |

Total expected BQ cost: **$3-8** on full refresh (first run), $0.2-1 on reruns. The $10 threshold in the cost estimator is the automatic gate; any single step projected above it halts for user approval.

## Critical Files to Modify/Create

**Copy (full fork)**:
- `Empirics/dataform/definitions/**/*.sqlx` → `paper_first_draft/dataform/definitions/**/*.sqlx`
- `Empirics/dataform/workflow_settings.yaml` → `paper_first_draft/dataform/workflow_settings.yaml` (bump `defaultDataset` suffixes to `_apr16` so the fork does not overwrite production)

**New files**:
- `paper_first_draft/dataform/definitions/ref/nagaraj_yao_region_map.sqlx`
- `paper_first_draft/dataform/definitions/stage/pat_family_forward_citations.sqlx`
- `paper_first_draft/dataform/definitions/stage/clinical_trial_core.sqlx`
- `paper_first_draft/dataform/definitions/int/pat_family_citation_quantile_flags.sqlx`
- `paper_first_draft/dataform/definitions/int/ct_country_quarter_measures.sqlx`
- `paper_first_draft/dataform/definitions/int/grant_country_quarter_measures.sqlx`
- `paper_first_draft/dataform/definitions/assertions/assert_quantile_distribution.sqlx`
- `paper_first_draft/dataform/definitions/assertions/assert_trial_bounds.sqlx`
- `paper_first_draft/dataform/definitions/assertions/assert_world_totals_monotone.sqlx`
- `paper_first_draft/dataform/definitions/assertions/assert_union3_bounds.sqlx`
- `paper_first_draft/code/*.py` (14 files per §Python Figure Generators + orchestration)
- `paper_first_draft/code/config_apr16.yaml`
- `paper_first_draft/quality_reports/specs/2026-04-16_paper_first_draft_spec.md`
- `paper_first_draft/logs/README.md`
- `paper_first_draft/quality_reports/decisions/decision_log.md`
- `paper_first_draft/README.md`
- Memory: `memory/project_paper_first_draft.md` + MEMORY.md index entry

**Modify (in the fork only; production copy untouched)**:
- `paper_first_draft/dataform/definitions/int/global_quarter_totals.sqlx` (+9 cols)
- `paper_first_draft/dataform/definitions/int/pub_6way_decomp_ctq.sqlx` (+3 union-3 cols)
- `paper_first_draft/dataform/definitions/int/pat_6way_fund_decomp_ctq.sqlx` (+3 union-3 cols)
- `paper_first_draft/dataform/definitions/mart/panel_country_quarter_wide.sqlx` (+12 cols)
- `paper_first_draft/dataform/definitions/stage/pub_quality_features.sqlx` (push is_basic_pub into stage)

**Reused (read-only references, never modified)**:
- `Empirics/dataform/definitions/int/pat_6way_fund_decomp_ctq.sqlx:17-25` (UNION DISTINCT logic template)
- `Empirics/dataform/definitions/stage/pub_pub_country_base.sqlx` (`w_aff = 1/len(country_codes)` fractional attribution)
- `geography_gov_innovation_paper/code/world_share_section.py` (plotting primitives to port + extend)
- `geography_gov_innovation_paper/code/decomposition_engine.py` (region aggregation)
- `geography_gov_innovation_paper/code/report_config_apr11.yaml` (registry template)
- `.claude/commands/{coordinator, data-pipeline-runner, verifier, referee, reproducibility-validator, research-design-auditor}.md` (agent contracts; do NOT modify)
- `.claude/skills/{checkin, done, run-pipeline, cross-file-check, merge-audit, compile-latex, figure-style, pre-submission, replication-package-builder}.md` (skill contracts; do NOT modify)
- `AGENTS.md` (quality gates A-F and P0-P4 severity)

## Verification

1. **Dataform assertions** (automatic gate at Stage 3): all 9 pass
2. **Shape sanity**: panel = 36 countries × ~172 quarters ≈ 6.2k rows; world totals ≈ 180 rows
3. **Nagaraj/Yao visual match**: `outputs/validation/ny_fig1b_overlay.png` — overlay Fig 1 top-left and top-right on N-Y's published series at 5-year grid points. Accept ±5pp; alarm at ±10pp
4. **Rest-of-World consistency**: for every year, `sum(5 region shares) == 1.0 ± 0.001`
5. **Union-3 consistency**: `pat_union3_govfund_ctq ≤ sum(tiers)` (upper bound); `≥ pat_govfund_direct_ctq` (lower bound)
6. **Reproducibility** (Gate E): `generate_all_figures.py --from-scratch` reproduces every PDF from the two CSVs deterministically (<10 min) — validated by `/reproducibility-validator`
7. **Referee sign-off**: 5 reports in `paper_first_draft/quality_reports/referee/` with zero unaddressed P0-P1 findings
8. **Cross-file consistency** (Gate A): `cross-file-check` passes on SQLX ↔ config_apr16.yaml ↔ panel CSV ↔ paper.tex
9. **Figure style** (Gate F): `figure-style` passes on all 9 figures (axis labels, DPI, color scheme, fonts, caption format)
10. **End-to-end**: `pdflatex paper.tex` produces `paper.pdf` with all 9 figures at ≥300 DPI

## Improvement Summary (vs. original Plan Apr16.docx)

1. **Corrected starting point**: original plan references "apr11 researcher/org matching"; confirmed the canonical is `panel_country_quarter_wide_apr_11.csv` + `report_config_apr11.yaml`, and the latest artifact is `gov_innovation_slides_apr14.tex` (not `apr11`). Plan now builds on those explicitly.
2. **Resolved figure-spec ambiguities**: Fig 3 typo ("university assignee"→"government assignee"), Fig 6 layout (1×2 confirmed), Fig 7 layout (fully spelled out with RID/INST/overlay/union), Fig 9 typos (patents not publications; 14 countries enumerated).
3. **Operationalized patent top-5%**: original plan left IPC level, year basis, jurisdiction scope, and citation window unspecified; now = IPC-4 × app-year × rep-doc jurisdiction × 5y-forward, matching Fleming/Hall-Jaffe-Trajtenberg conventions.
4. **Simplified regional strategy**: eliminated the "Rest of M/LI" panel extension in favor of `Rest of World = world_total − (US + EU + Rest HI + China)` residual — cuts ~10 countries of new Dimensions extraction (~$3-5 BQ saving + faster materialization) while preserving visual completeness.
5. **Explicit union-3 pass-through**: three new pass-through columns per 6-way decomp prevent Python-side double-count bugs.
6. **Extended time window**: original plan wants 1980-2022, but current `cs_*` figures are 2000-2024. Plan extends generators; Dataform already covers 1950-2024.
7. **Cost-gated execution**: `cost_estimator.py` with $10 hard gate and `cost_log.csv` operationalizes "ask before >$10" rule with real data.
8. **Staged checkpoints**: 10 stages with 5 user-visible gates for cheap mid-stream course-correction.
9. **Fractional-attribution honesty**: fractional throughout; documents ~3-5pp delta vs. N-Y with a validation overlay in `outputs/validation/`.
10. **New assertions**: 4 Dataform assertion files catch quantile drift, trial-bounds violations, world-totals-monotone breaks, and union-3 double-counts at every Dataform run.
11. **Dataform optimization**: partition/cluster/incremental recommendations without touching the fuzzy-matching hot path.
12. **Worldwide denominators completed**: `global_quarter_totals` extended with 9 new columns so every figure has a true worldwide denominator; Fig 4/5 become feasible.
13. **Integration with existing agent/skill catalog**: every stage is executed through a named agent or skill already in `.claude/commands/` and `.claude/skills/`, so quality gates A-F in `AGENTS.md` are automatically enforced; `/referee` picks up the paper via a new spec file rather than a bespoke subagent — fewer moving parts, leveraged institutional machinery.
14. **Log organization discipline**: dedicated `paper_first_draft/logs/` hierarchy (dataform/cost/downloads/figure_generation/tex_compile/session), plus mirrored `paper_first_draft/quality_reports/` for structured quality artifacts. Every log entry is append-only and timestamp-prefixed so any `/checkin` can reconstruct progress.
15. **Memory discipline**: one labeled memory file `project_paper_first_draft.md` (type: project) with key decisions, execution state, open items — updated after each stage end by `/done` — and a single concise line in `MEMORY.md`. No duplication, no stale entries.

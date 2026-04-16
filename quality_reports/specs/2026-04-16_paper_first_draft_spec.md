# Spec: paper_first_draft (Geography of Gov Innovation)

**Type**: referee-scope extension (read by existing `/referee` agent)
**Created**: 2026-04-16
**Authority**: supersedes `referee.md` review-focus defaults only for deliverables under `paper_first_draft/`

## Literature bindings (read in full before reviewing)

- `Empirics/Literature/w34694 (1).pdf` — Nagaraj & Yao "Geography of Science" (NBER 2026, publications only, 1980-2022)
- `Empirics/Literature/Public_innovation_Surico.pdf` — Gazzani, Martinez, Natoli, Surico "The Public Origins of American Innovation" (NBER 2026)
- `Empirics/Literature/science.aaw2373.pdf` — Fleming, Greene, Li, Marx, Yao "Government-funded research increasingly fuels innovation" (Science 2019)
- `Empirics/Literature/aaw2373_fleming_sm.pdf` — Fleming et al. supplementary materials

## Paper scope

Nine figures in `paper_first_draft/outputs/figures/fig1..fig9.{pdf,png,jpg}` plus `paper.tex` compiled to `paper.pdf`, documenting the global footprint of government-funded innovation 1980-2022 (Fig 8-9 restricted to 2000-2022).

## Review focus (in addition to AGENTS.md quality gates A-F)

1. **Fractional vs. random attribution**: Our figures use fractional multi-affiliation attribution throughout. Nagaraj/Yao use random-single-affiliation selection for their Figure 1b. We expect a 3-5pp divergence. Referee must verify the figure note discloses this and the validation overlay at `outputs/validation/ny_fig1b_overlay.png` shows acceptable agreement (±5pp; alarm at ±10pp).

2. **Top-5% patent quantile** (`pat_family_citation_quantile_flags`):
   - Tech class: IPC-4 (first four chars of primary IPC)
   - Year basis: family application year (from `patent_family_anchor.family_app_qtr`)
   - Jurisdiction: anchor/rep-doc jurisdiction (one per family)
   - Forward-cite window: 5 years post-filing (truncated to avoid age bias, Fleming/Hall-Jaffe-Trajtenberg standard)
   - Cell fallback: `(ipc4, app_year)` when primary `(ipc4, app_year, jurisdiction)` has <20 families
   - Referee must verify the 5% share holds to ±2pp per year (checked by `assert_quantile_distribution`).

3. **Basic-research FoR rollup** (`for2_basic_research_map`):
   - FoR2 divisions 31, 34, 37, 41, 49, 51 = basic (Biological, Chemical, Earth, Environmental, Mathematical, Physical Sciences)
   - Applied at patent family level via FoR4→FoR2 `SUBSTR(code, 1, 2)` with majority rule
   - Referee must verify this mapping is defensible against OECD Frascati definitions (basic = research undertaken primarily to acquire new knowledge without specific application in view).

4. **Union-3 de-duplication** (`pub_union3_govfund_*` + `pat_union3_govfund_*`):
   - `UNION DISTINCT` over `(family_id|pub_id, country_code)` across direct, RID, INST tiers
   - Fractional attribution preserved via `w_aff` (pubs) and `w_domestic` (patents)
   - Fig 7 validation overlay interpretable: RID+INST methods produce a share comparable to direct-link share (verifies the matching procedure)
   - Referee must verify `assert_union3_bounds` passes and Fig 7 bottom-left caption is clear.

5. **Nagaraj/Yao region mapping** (`ref/nagaraj_yao_region_map`):
   - US = [US]
   - EU = EU-27 + UK + EFTA, panel intersection, time-invariant 1980-2022
   - Rest HI = [JP, KR, CA, AU, IL, NZ, CL]
   - China = [CN]
   - Rest of World = residual from worldwide totals (not explicitly enumerated)
   - Panel members not in any of the four explicit regions (MX, TR, CO, CR) flow into Rest-of-World via residual
   - Referee must verify region sums reconcile to 1.0 ± 0.001 per year.

6. **Clinical-trial gov classification** (`clinical_trial_core.is_gov_sponsor`):
   - Sponsor-based (not funder-based): TRUE if any sponsor GRID is in gov_org_whitelist OR has is_gov_surico=TRUE
   - Fractional attribution by sponsor country (`w_aff = 1 / len(research_org_countries)`)
   - Basic research for trials currently emits zero (FoR classification of trials is not yet implemented); referee should flag as P3 (deferred improvement) unless adequate alternative exists.

7. **Surico et al. concordance**:
   - Surico's three categories: (1) gov-funded privately-owned, (2) privately-funded privately-owned, (3) publicly-funded publicly-owned
   - Our 6-way mapping: gov_owned ≈ (3), uni_govfund + private_govfund ≈ (1), uni_no_govfund + private_no_govfund ≈ (2), unclassified = residual
   - Referee must verify the mapping is discussed in Section "Related Literature" of the paper and any deviations flagged.

## Deliverable paths reviewed

- `paper_first_draft/outputs/figures/fig{1..9}.pdf`
- `paper_first_draft/outputs/paper.pdf` and `paper.tex`
- `paper_first_draft/data/panel_country_quarter_wide_apr16.csv`
- `paper_first_draft/data/world_quarter_totals_apr16.csv`
- `paper_first_draft/dataform/definitions/{ref,stage,int,mart,assertions}/*.sqlx` (new + modified only — see plan for list)
- `paper_first_draft/code/*.py`

## Output path

`paper_first_draft/quality_reports/referee/YYYY-MM-DD_<stage>.md`

Five scheduled checkpoints:
- `YYYY-MM-DD_fig1-3.md` — after first figure set
- `YYYY-MM-DD_fig4-5.md`
- `YYYY-MM-DD_fig6-7.md`
- `YYYY-MM-DD_fig8-9.md`
- `YYYY-MM-DD_paper_full.md` — full referee pass on paper.pdf

Each report inherits the standard `/referee` output contract: verdict (SHIP/REVISE/MAJOR_REDESIGN), summary, ranked concerns by P0-P4 severity, review categories (theoretical, empirical, computational, presentation, internal consistency, methodology, literature positioning), resolved non-issues, shipping recommendation.

## Invocation from coordinator

When invoking `/referee` for paper_first_draft work, pass this spec file explicitly:

```
/referee paper_first_draft/quality_reports/specs/2026-04-16_paper_first_draft_spec.md <stage>
```

This ensures the referee binds to the literature + review focus listed above in addition to its own default scope from `.claude/commands/referee.md`.

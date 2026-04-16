"""Compile paper.tex from the figure set. Minimal scaffold -- expand captions as you go."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


TEMPLATE = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{booktabs}
\graphicspath{{figures/}}

\title{Geography of Government-Funded Innovation: Nine Descriptive Figures\thanks{Paper first draft, apr16. See paper_first_draft/quality_reports/plans/ for methodology.}}
\author{J.~Sam.~[placeholder]}
\date{\today}

\begin{document}
\maketitle

\section{Overview}
This paper presents nine descriptive figures documenting the global footprint of
government-funded innovation across publications, patents, grants, and clinical
trials from 1980 to 2022. The framework extends Nagaraj \& Yao (2026) to patents,
grants, and trials, and builds on Surico et al.\ (2026) for the government-funding
decomposition.

\section{Figures}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig1}
  \caption{World share of publications (top row) and patents (bottom row) in the full
  sample, basic research subset, and top 5\% quality tier. Regions follow Nagaraj
  \& Yao's five-region taxonomy (US, EU, Rest high-income, China, Rest of World).
  Attribution is fractional throughout (contrasting with Nagaraj \& Yao's random
  single-affiliation assignment); the $\sim 3$-$5$ pp difference from their
  Figure~1b is documented in the validation overlay.}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig2}
  \caption{Same axes as Figure~1, restricted to university-owned outputs.}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig3}
  \caption{Same axes as Figure~1, restricted to government-owned outputs (whitelisted
  government assignee or affiliation).}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig4}
  \caption{World share of grants attributed by research-organization country.
  Panels: total, basic research subset, government-funder subset, non-government-funder subset.}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig5}
  \caption{World share of clinical trials by sponsor country (fractional). Total and
  government-sponsored subset.}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig6}
  \caption{US patents: share that is government-owned, and share of
  privately-owned patents with a direct government-funding linkage in Dimensions.
  Both use total US patents as denominator.}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig7}
  \caption{US patents: 3-tier government-funding linkage. Top row: researcher-ID
  linked, institution linked (both plausible linkages). Bottom-left: validation
  overlay comparing \{RID + INST\} to direct-link share. Bottom-right: union of
  all three tiers, de-duplicated.}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig8}
  \caption{Publications: union-of-three-tier government-funded share of worldwide
  publications, 2000-2022, for US, EU, and China. Panels: all / top 5\% journals
  / basic research.}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{fig9}
  \caption{Patents: union-of-three-tier government-funded share of worldwide
  patents, 2000-2022, for 14 countries with available data: AU, AT, BE, CA, CN,
  CZ, DE, IT, JP, PT, SI, CH, GB, US. Panels: all / top 5\% (forward citations,
  normalized by IPC-4 $\times$ app-year $\times$ jurisdiction) / basic research.}
\end{figure}

\end{document}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile", action="store_true", help="Run pdflatex after writing")
    args = parser.parse_args()

    out_dir = Path(__file__).parent.parent / "outputs"
    tex = out_dir / "paper.tex"
    tex.write_text(TEMPLATE)
    print(f"Wrote {tex}")

    if args.compile:
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper.tex"], cwd=out_dir, check=False)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper.tex"], cwd=out_dir, check=False)
        print("Compilation attempted. Check outputs/paper.pdf.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

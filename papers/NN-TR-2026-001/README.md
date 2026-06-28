# NN-TR-2026-001

`nyanya LLM：面向碳基神经协同与有机认知代谢的全模态基础模型`

This directory contains the first formal nya-lab technical report — a comprehensive 13-section paper covering distributed cognitive coordination architecture, organic cognitive metabolism, coordination scaling laws, and experimental validation.

## Files

- `paper.tex` - LaTeX source.
- `paper.typ` - Chinese Typst source (authoritative expanded version).
- `build_pdf.py` - current Chinese PDF generator using ReportLab.
- `references.bib` - real references only.
- `paper.md` - readable Markdown draft (English expanded version).
- `Makefile` - local build helper.

## Authoritative Version

The definitive Chinese version is maintained at `docs/research/NN-TR-2026-001.md`. Both `paper.typ` and `paper.md` are derived from this source.

## Build

The current build uses ReportLab for Chinese PDF output.

```sh
make
```

Typst and LaTeX sources are retained as secondary formats:

```sh
make typst
make tex
```
LATEX ?= pdflatex
BIBTEX ?= bibtex
TARGET := paper
TYPST ?= typst
PYTHON ?= /Users/joyfor/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3

.PHONY: all pdf typst tex clean check check-tex

all: pdf

pdf:
	$(PYTHON) build_pdf.py

typst:
	@command -v $(TYPST) >/dev/null 2>&1 || { echo "Missing Typst CLI: $(TYPST)"; exit 1; }
	$(TYPST) compile $(TARGET).typ $(TARGET).pdf

tex: check-tex
	$(LATEX) $(TARGET).tex
	$(BIBTEX) $(TARGET)
	$(LATEX) $(TARGET).tex
	$(LATEX) $(TARGET).tex

check: pdf

check-tex:
	@command -v $(LATEX) >/dev/null 2>&1 || { echo "Missing LaTeX engine: $(LATEX)"; exit 1; }
	@command -v $(BIBTEX) >/dev/null 2>&1 || { echo "Missing BibTeX: $(BIBTEX)"; exit 1; }

clean:
	rm -f $(TARGET).aux $(TARGET).bbl $(TARGET).blg $(TARGET).log $(TARGET).out $(TARGET).pdf
	rm -f ../../output/pdf/VR-TR-2026-001-cn.pdf

PYTHON ?= python

.PHONY: download prepare audit ate uplift figures test all

download:
	$(PYTHON) -m src.download_data

prepare:
	$(PYTHON) -m src.prepare_data

audit:
	$(PYTHON) -m src.audit

ate:
	$(PYTHON) -m src.estimate_ate

uplift:
	$(PYTHON) -m src.uplift_policy

figures:
	$(PYTHON) -m src.build_figures
	$(PYTHON) -m src.build_dashboard

test:
	pytest -q

all: download prepare audit ate uplift figures test

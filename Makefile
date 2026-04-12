PY ?= python
BASE_DIR ?= artifacts/economy_baseline
VERSION ?= economy_v1_local
OLD ?= economy_v1_testA
NEW ?= economy_v1_testB
DIFF_JSON ?= /tmp/economy_diff_$(OLD)_$(NEW).json
DIFF_MD ?= /tmp/economy_diff_$(OLD)_$(NEW).md
DASH_HTML ?= /tmp/economy_dashboard_$(NEW).html

.PHONY: economy-smoke economy-freeze economy-compare economy-dashboard economy-report

economy-smoke:
	$(PY) -m py_compile tools/economy_lab.py tools/run_economy_baseline.py tools/compare_economy_baselines.py tools/economy_dashboard.py

economy-freeze:
	$(PY) tools/run_economy_baseline.py --version $(VERSION) --out-dir $(BASE_DIR)

economy-compare:
	$(PY) tools/compare_economy_baselines.py --base-dir $(BASE_DIR) --old-version $(OLD) --new-version $(NEW) --out-json $(DIFF_JSON) --out-md $(DIFF_MD)

economy-dashboard:
	$(PY) tools/economy_dashboard.py --suite-json $(BASE_DIR)/$(NEW)/suite.json --diff-json $(DIFF_JSON) --out-html $(DASH_HTML) --title "Economy Dashboard $(NEW)"

economy-report: economy-smoke economy-freeze
	@echo "[ok] baseline congelado para VERSION=$(VERSION)"

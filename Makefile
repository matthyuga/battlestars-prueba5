PY ?= python
BASE_DIR ?= artifacts/economy_baseline
VERSION ?= economy_v1_local
OLD ?= economy_v1_testA
NEW ?= economy_v1_testB
DIFF_JSON ?= /tmp/economy_diff_$(OLD)_$(NEW).json
DIFF_MD ?= /tmp/economy_diff_$(OLD)_$(NEW).md
DASH_HTML ?= /tmp/economy_dashboard_$(NEW).html
THRESHOLDS_FILE ?= tools/scenarios/economy_alert_thresholds.json

.PHONY: economy-smoke economy-freeze economy-compare economy-dashboard economy-report economy-gate economy-cycle economy-exe

economy-smoke:
	$(PY) -m py_compile tools/economy_lab.py tools/run_economy_baseline.py tools/compare_economy_baselines.py tools/economy_dashboard.py tools/economy_toolkit.py

economy-freeze:
	$(PY) tools/run_economy_baseline.py --version $(VERSION) --out-dir $(BASE_DIR)

economy-compare:
	$(PY) tools/compare_economy_baselines.py --base-dir $(BASE_DIR) --old-version $(OLD) --new-version $(NEW) --thresholds-file $(THRESHOLDS_FILE) --out-json $(DIFF_JSON) --out-md $(DIFF_MD)

economy-gate:
	$(PY) tools/compare_economy_baselines.py --base-dir $(BASE_DIR) --old-version $(OLD) --new-version $(NEW) --thresholds-file $(THRESHOLDS_FILE) --fail-on-alert --out-json $(DIFF_JSON) --out-md $(DIFF_MD)

economy-dashboard:
	$(PY) tools/economy_dashboard.py --suite-json $(BASE_DIR)/$(NEW)/suite.json --diff-json $(DIFF_JSON) --out-html $(DASH_HTML) --title "Economy Dashboard $(NEW)"

economy-report: economy-smoke economy-freeze
	@echo "[ok] baseline congelado para VERSION=$(VERSION)"

economy-cycle:
	$(PY) tools/economy_toolkit.py cycle --version $(NEW) --previous-version $(OLD) --base-dir $(BASE_DIR) --thresholds-file $(THRESHOLDS_FILE) --out-json $(DIFF_JSON) --out-md $(DIFF_MD) --out-html $(DASH_HTML)


economy-exe:
	$(PY) tools/build_economy_toolkit_executable.py

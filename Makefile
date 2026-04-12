PY ?= python
BASE_DIR ?= artifacts/economy_baseline
VERSION ?= economy_v1_local
OLD ?= economy_v1_testA
NEW ?= economy_v1_testB
DIFF_JSON ?= /tmp/economy_diff_$(OLD)_$(NEW).json
DIFF_MD ?= /tmp/economy_diff_$(OLD)_$(NEW).md
DASH_HTML ?= /tmp/economy_dashboard_$(NEW).html
THRESHOLDS_FILE ?= tools/scenarios/economy_alert_thresholds.json

.PHONY: economy-smoke economy-freeze economy-compare economy-dashboard economy-report economy-gate economy-cycle economy-exe economy-release-package economy-verify-checksum economy-wizard economy-profile-list economy-run-profile economy-doctor economy-preflight economy-ci-metrics

economy-smoke:
	$(PY) -m py_compile tools/economy_lab.py tools/run_economy_baseline.py tools/compare_economy_baselines.py tools/economy_dashboard.py tools/economy_toolkit.py tools/generate_economy_ci_metrics.py

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

economy-release-package:
	$(PY) tools/package_economy_toolkit_release.py

# Usage: make economy-verify-checksum PACKAGE=dist/release/<file>.zip CHECKSUM=dist/release/<file>.zip.sha256
economy-verify-checksum:
	$(PY) tools/verify_release_checksum.py --package $(PACKAGE) --checksum-file $(CHECKSUM)

economy-wizard:
	$(PY) tools/economy_toolkit.py wizard

economy-profile-list:
	$(PY) tools/economy_toolkit.py profile-list

# Usage: make economy-run-profile PROFILE=balance_default VERSION=economy_v2 PREVIOUS=economy_v1
economy-run-profile:
	$(PY) tools/economy_toolkit.py run-profile --name $(PROFILE) --version $(VERSION) --previous-version $(PREVIOUS)

economy-doctor:
	$(PY) tools/economy_toolkit.py doctor

economy-preflight: economy-smoke
	$(PY) -m pytest -q
	$(PY) tools/economy_toolkit.py doctor


# Usage: make economy-ci-metrics DIFF_JSON=/tmp/economy_diff_ci.json OUT_JSON=/tmp/economy_ci_metrics.json
OUT_JSON ?= /tmp/economy_ci_metrics.json
economy-ci-metrics:
	$(PY) tools/generate_economy_ci_metrics.py --diff-json $(DIFF_JSON) --out-json $(OUT_JSON)

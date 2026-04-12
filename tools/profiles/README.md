# Economy Toolkit Profiles

Formato JSON esperado:

```json
{
  "name": "balance_default",
  "description": "texto",
  "base_dir": "artifacts/economy_baseline",
  "thresholds_file": "tools/scenarios/economy_alert_thresholds.json",
  "title": "Economy Dashboard",
  "fail_on_alert": false,
  "bundle_dir": "artifacts/economy_reports",
  "version": "economy_v_next",
  "previous_version": "economy_v_prev"
}
```

Uso:

```bash
python tools/economy_toolkit.py profile-list
python tools/economy_toolkit.py run-profile --name balance_default --version economy_v2 --previous-version economy_v1
```

from tools import economy_toolkit as tk


def test_wizard_guided_flow_invokes_cycle_bundle(monkeypatch):
    answers = iter([
        "2",                    # opción flujo guiado
        "economy_v_new",       # version
        "economy_v_old",       # previous
        "artifacts/economy_baseline",
        "tools/scenarios/economy_alert_thresholds.json",
        "n",                    # fail_on_alert
        "artifacts/economy_reports",
        "bundle_test",
        "Dashboard Test",
    ])

    monkeypatch.setattr("builtins.input", lambda _msg="": next(answers))

    called = {}

    def fake_run_cycle_and_bundle(py, version, previous_version, base_dir, thresholds_file, out_json, out_md, out_html, title, fail_on_alert, bundle_dir, bundle_name):
        called.update({
            "version": version,
            "previous_version": previous_version,
            "base_dir": base_dir,
            "thresholds_file": thresholds_file,
            "title": title,
            "fail_on_alert": fail_on_alert,
            "bundle_dir": bundle_dir,
            "bundle_name": bundle_name,
        })
        return 0

    monkeypatch.setattr(tk, "run_cycle_and_bundle", fake_run_cycle_and_bundle)

    rc = tk.run_wizard(py="python")
    assert rc == 0
    assert called["version"] == "economy_v_new"
    assert called["previous_version"] == "economy_v_old"
    assert called["bundle_name"] == "bundle_test"
    assert called["fail_on_alert"] is False

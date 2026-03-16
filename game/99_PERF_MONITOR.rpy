# ============================================================
# 99_PERF_MONITOR.rpy
# Overlay simple de rendimiento en tiempo real (FPS / frame time)
# Ren'Py 7.4.9 compatible
# ============================================================

default perf_monitor_visible = False
default perf_monitor_update_sec = 0.05
default perf_monitor_window = []
default perf_monitor_window_size = 30

default perf_monitor_stats = {
    "fps": 0.0,
    "frame_ms": 0.0,
    "tick_ms": 0.0,
    "sample_count": 0,
    "renderer": "n/a",
}

init -920 python:
    import time
    import renpy.store as S
    import renpy.exports as R

    _perf_last_wall = None

    def perf_monitor_toggle():
        S.perf_monitor_visible = not bool(getattr(S, "perf_monitor_visible", False))
        try:
            R.restart_interaction()
        except:
            pass

    def perf_monitor_tick(dt=0.05):
        global _perf_last_wall

        t0 = time.time()

        try:
            fps = float(R.get_fps())
        except:
            fps = 0.0

        if fps <= 0.0:
            now = time.time()
            if _perf_last_wall is None:
                _perf_last_wall = now
            elapsed = max(0.0001, now - _perf_last_wall)
            _perf_last_wall = now
            fps = 1.0 / elapsed

        frame_ms = (1000.0 / fps) if fps > 0.0001 else 0.0

        try:
            info = R.get_renderer_info() or {}
            renderer = str(info.get("renderer", "n/a") or "n/a")
        except:
            renderer = "n/a"

        win = getattr(S, "perf_monitor_window", [])
        if not isinstance(win, list):
            win = []
        win.append(float(frame_ms))
        try:
            maxn = max(5, int(getattr(S, "perf_monitor_window_size", 30) or 30))
        except:
            maxn = 30
        if len(win) > maxn:
            win = win[-maxn:]
        S.perf_monitor_window = win

        avg_ms = (sum(win) / float(len(win))) if len(win) > 0 else float(frame_ms)

        try:
            wsorted = sorted(win)
            idx95 = int((len(wsorted) - 1) * 0.95)
            p95_ms = float(wsorted[max(0, min(len(wsorted) - 1, idx95))]) if len(wsorted) > 0 else float(frame_ms)
        except:
            p95_ms = float(frame_ms)

        tick_ms = max(0.0, (time.time() - t0) * 1000.0)

        st = getattr(S, "perf_monitor_stats", {})
        if not isinstance(st, dict):
            st = {}
        st["fps"] = float(fps)
        st["frame_ms"] = float(frame_ms)
        st["avg_frame_ms"] = float(avg_ms)
        st["p95_frame_ms"] = float(p95_ms)
        st["tick_ms"] = float(tick_ms)
        st["sample_count"] = int(st.get("sample_count", 0) or 0) + 1
        st["renderer"] = renderer
        S.perf_monitor_stats = st

    S.perf_monitor_toggle = perf_monitor_toggle
    S.perf_monitor_tick = perf_monitor_tick


screen perf_monitor_overlay():
    zorder 200
    modal False

    if perf_monitor_visible:
        $ _st = perf_monitor_stats if isinstance(perf_monitor_stats, dict) else {}
        $ _fps = float(_st.get("fps", 0.0) or 0.0)
        $ _fms = float(_st.get("frame_ms", 0.0) or 0.0)
        $ _avg = float(_st.get("avg_frame_ms", 0.0) or 0.0)
        $ _p95 = float(_st.get("p95_frame_ms", 0.0) or 0.0)
        $ _tms = float(_st.get("tick_ms", 0.0) or 0.0)
        $ _samples = int(_st.get("sample_count", 0) or 0)
        $ _renderer = str(_st.get("renderer", "n/a") or "n/a")
        $ _upd = float(getattr(store, "perf_monitor_update_sec", 0.05) or 0.05)

        timer _upd repeat True action Function(getattr(store, "perf_monitor_tick", None), _upd)

        frame:
            background "#00131CDD"
            xalign 1.0
            yalign 0.0
            xpadding 10
            ypadding 8
            xoffset -8
            yoffset 8

            vbox:
                spacing 4
                text "PERF MONITOR (F10)" size 14 color "#80DEEA" bold True
                text "FPS: {:.1f}".format(_fps) size 13 color "#FFFFFF"
                text "Frame: {:.2f} ms".format(_fms) size 13 color "#C5E1A5"
                text "Avg(30): {:.2f} ms".format(_avg) size 12 color "#AED581"
                text "P95(30): {:.2f} ms".format(_p95) size 12 color "#FFCC80"
                text "Tick: {:.3f} ms".format(_tms) size 12 color "#B0BEC5"
                text "Samples: {}".format(_samples) size 12 color "#B0BEC5"
                text "Renderer: {}".format(_renderer) size 12 color "#B0BEC5"

init 998 python:
    if "perf_monitor_overlay" not in config.overlay_screens:
        config.overlay_screens.append("perf_monitor_overlay")


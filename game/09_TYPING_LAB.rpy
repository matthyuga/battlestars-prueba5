# Minijuego aislado para practicar mecanografía (sin depender de contraataque).

init -850 python:
    import renpy.store as S

    def typing_lab_default_state():
        return {
            "active": False,
            "sequence": [],
            "total": 0,
            "index": 0,
            "current_letter": "",
            "seconds_per_letter": 2.0,
            "time_left": 0.0,
            "last_status": "idle",   # idle|active|hit|wrong|timeout|success|fail
            "feedback_time_left": 0.0,
            "pending_next_index": None,
            "hits": 0,
            "misses": 0,
            "required_hits": 6,
            "result": None,
        }

    def typing_lab_generate_sequence(total_letters=10):
        import random
        letters = list("abcdefghijklmnopqrstuvwxyz")
        try:
            n = int(total_letters)
        except:
            n = 10
        n = max(1, n)
        return [random.choice(letters) for _ in range(n)]

    def typing_lab_prepare(total_letters=10, seconds_per_letter=2.0, required_hits=6):
        seq = typing_lab_generate_sequence(total_letters=total_letters)
        try:
            spl = float(seconds_per_letter)
        except:
            spl = 2.0
        spl = max(2.0, spl)

        try:
            req = int(required_hits)
        except:
            req = 6
        req = max(1, req)

        st = {
            "active": True,
            "sequence": list(seq),
            "total": int(len(seq)),
            "index": 0,
            "current_letter": str(seq[0] if seq else "a"),
            "seconds_per_letter": float(spl),
            "time_left": float(spl),
            "last_status": "active",
            "feedback_time_left": 0.0,
            "pending_next_index": None,
            "hits": 0,
            "misses": 0,
            "required_hits": int(req),
            "result": None,
        }
        S.typing_lab_state = st
        return dict(st)

    def typing_lab_finalize_if_needed(st):
        if not isinstance(st, dict):
            st = typing_lab_default_state()

        total = int(st.get("total", 0) or 0)
        idx = int(st.get("index", 0) or 0)

        if idx >= total:
            hits = int(st.get("hits", 0) or 0)
            misses = int(st.get("misses", 0) or 0)
            req = int(st.get("required_hits", 6) or 6)
            ok = bool(hits >= req)
            st["active"] = False
            st["last_status"] = ("success" if ok else "fail")
            st["result"] = {
                "executed": True,
                "success": bool(ok),
                "reason": ("completed" if ok else "insufficient_hits"),
                "hits": int(hits),
                "misses": int(misses),
                "required_hits": int(req),
                "total_letters": int(total),
            }
            st["current_letter"] = ""
            st["time_left"] = 0.0

        S.typing_lab_state = st
        return dict(st)

    def typing_lab_tick(dt=0.02):
        st = getattr(S, "typing_lab_state", None)
        if not isinstance(st, dict):
            st = typing_lab_default_state()

        if isinstance(st.get("result"), dict):
            return dict(st)

        try:
            delta = float(dt)
        except:
            delta = 0.02
        if delta <= 0.0:
            delta = 0.02

        fb = float(st.get("feedback_time_left", 0.0) or 0.0)
        if fb > 0.0:
            fb = max(0.0, fb - delta)
            st["feedback_time_left"] = fb
            if fb <= 0.0:
                next_idx = int(st.get("pending_next_index", -1) or -1)
                if next_idx >= 0:
                    st["index"] = int(next_idx)
                    st["pending_next_index"] = None
                    st = typing_lab_finalize_if_needed(st)
                    if not isinstance(st.get("result"), dict):
                        seq = list(st.get("sequence", []) or [])
                        idx = int(st.get("index", 0) or 0)
                        if 0 <= idx < len(seq):
                            spl = float(st.get("seconds_per_letter", 2.0) or 2.0)
                            st["current_letter"] = str(seq[idx])
                            st["time_left"] = float(spl)
                            st["last_status"] = "active"
            S.typing_lab_state = st
            return dict(st)

        if not bool(st.get("active", False)):
            return typing_lab_finalize_if_needed(st)

        left = float(st.get("time_left", 0.0) or 0.0)
        left = max(0.0, left - delta)
        st["time_left"] = left

        if left <= 0.0:
            idx = int(st.get("index", 0) or 0)
            st["last_status"] = "timeout"
            st["misses"] = int(st.get("misses", 0) or 0) + 1
            st["pending_next_index"] = int(idx + 1)
            st["feedback_time_left"] = 0.20

        S.typing_lab_state = st
        return dict(st)

    def typing_lab_press_key(key_text=""):
        st = getattr(S, "typing_lab_state", None)
        if not isinstance(st, dict):
            st = typing_lab_default_state()

        if isinstance(st.get("result"), dict):
            return dict(st)
        if float(st.get("feedback_time_left", 0.0) or 0.0) > 0.0:
            return dict(st)

        seq = list(st.get("sequence", []) or [])
        idx = int(st.get("index", 0) or 0)
        if idx < 0 or idx >= len(seq):
            return dict(st)

        expected = str(seq[idx] or "").lower()
        got = str(key_text or "").strip().lower()[:1]

        if not ("a" <= got <= "z"):
            return dict(st)

        if got == expected:
            st["last_status"] = "hit"
            st["hits"] = int(st.get("hits", 0) or 0) + 1
        else:
            st["last_status"] = "wrong"
            st["misses"] = int(st.get("misses", 0) or 0) + 1

        st["pending_next_index"] = int(idx + 1)
        st["feedback_time_left"] = 0.20
        S.typing_lab_state = st
        return dict(st)

    store.typing_lab_default_state = typing_lab_default_state
    store.typing_lab_prepare = typing_lab_prepare
    store.typing_lab_tick = typing_lab_tick
    store.typing_lab_press_key = typing_lab_press_key


screen typing_lab_qte():
    modal True
    zorder 260

    default _letters = "abcdefghijklmnopqrstuvwxyz"

    python:
        _st = getattr(store, "typing_lab_state", {})
        _cur = str(_st.get("current_letter", "") or "")
        _idx = int(_st.get("index", 0) or 0)
        _tot = int(_st.get("total", 0) or 0)
        _left = float(_st.get("time_left", 0.0) or 0.0)
        _hits = int(_st.get("hits", 0) or 0)
        _miss = int(_st.get("misses", 0) or 0)
        _req = int(_st.get("required_hits", 6) or 6)
        _status = str(_st.get("last_status", "active") or "active")
        _fb = float(_st.get("feedback_time_left", 0.0) or 0.0)
        _res = _st.get("result", None)

        if _status in ("wrong", "timeout", "fail"):
            _c = "#FF4D4D"
        elif _status in ("hit", "success"):
            _c = "#66FF99"
        else:
            _c = "#FFFFFF"

    timer 0.02 repeat True action Function(getattr(store, "typing_lab_tick", None), 0.02)

    if isinstance(_res, dict):
        timer 0.01 action Return(dict(_res))

    for _k in _letters:
        key _k action Function(getattr(store, "typing_lab_press_key", None), _k)

    add Solid("#000000")

    frame:
        background "#0000"
        xalign 0.5
        yalign 0.5
        xmaximum 860
        padding (28, 22)

        vbox:
            spacing 12

            text (_cur if _cur else "-"):
                xalign 0.5
                yalign 0.5
                size 120
                color _c
                bold True

            if _fb > 0.0:
                if _status == "hit":
                    text "ÉXITO" size 52 color "#66FF99" bold True xalign 0.5
                elif _status in ("wrong", "timeout"):
                    text "FALLO" size 52 color "#FF4D4D" bold True xalign 0.5

            text ("Letra %d/%d   %.2f s   ✔ %d / ✖ %d (mín %d)" % (int(_idx + 1), int(max(1, _tot)), float(_left), int(_hits), int(_miss), int(_req))):
                size 30
                color "#D0D0D0"
                xalign 0.5


screen typing_lab_result(_result=None):
    modal True
    zorder 260

    python:
        _r = _result if isinstance(_result, dict) else {}
        _hits = int(_r.get("hits", 0) or 0)
        _misses = int(_r.get("misses", 0) or 0)
        _req = int(_r.get("required_hits", 6) or 6)
        _tot = int(_r.get("total_letters", 10) or 10)
        _ok = bool(_r.get("success", False))
        _title = ("GANASTE" if _ok else "PERDISTE")
        _title_color = ("#66FF99" if _ok else "#FF4D4D")

    add Solid("#000000")

    frame:
        background "#0000"
        xalign 0.5
        yalign 0.5
        padding (24, 20)

        vbox:
            spacing 16

            text _title:
                size 72
                bold True
                color _title_color
                xalign 0.5

            text ("Resultado final: ✔ %d / ✖ %d · mínimo %d de %d" % (_hits, _misses, _req, _tot)):
                size 28
                color "#DDDDDD"
                xalign 0.5

            hbox:
                spacing 18
                xalign 0.5

                textbutton "Reintentar":
                    action [Hide("typing_lab_result"), Jump("typing_lab_start")]

                textbutton "Volver al menú":
                    action [Hide("typing_lab_result"), MainMenu()]


label typing_lab_start:
    $ typing_lab_prepare(total_letters=10, seconds_per_letter=2.0, required_hits=6)
    $ _typing_lab_result = renpy.call_screen("typing_lab_qte")
    call screen typing_lab_result(_typing_lab_result)
    return


default typing_lab_state = {
    "active": False,
    "sequence": [],
    "total": 0,
    "index": 0,
    "current_letter": "",
    "seconds_per_letter": 2.0,
    "time_left": 0.0,
    "last_status": "idle",
    "feedback_time_left": 0.0,
    "pending_next_index": None,
    "hits": 0,
    "misses": 0,
    "required_hits": 6,
    "result": None,
}

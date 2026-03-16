# Typing Lab aislado:
# - Fondo negro
# - Secuencia de 10 letras (a-z)
# - 2s por letra
# - Sin pantalla de perder
# - Si aciertas: verde y avanza
# - Si se acaba el tiempo: rojo y avanza

init -850 python:
    import random
    import renpy.store as S

    def typing_lab_default_state():
        return {
            "phase": "idle",         # idle | hit | timeout | done
            "sequence": [],
            "total": 10,
            "index": 0,
            "current_letter": "",
            "hits": 0,
            "seconds_per_letter": 2.0,
            "time_left": 2.0,
            "feedback_time_left": 0.0,
        }

    def typing_lab_prepare(total_letters=10, seconds_per_letter=2.0):
        letters = list("abcdefghijklmnopqrstuvwxyz")
        try:
            n = int(total_letters)
        except:
            n = 10
        n = max(1, n)

        try:
            spl = float(seconds_per_letter)
        except:
            spl = 2.0
        spl = max(0.2, spl)

        seq = [random.choice(letters) for _ in range(n)]

        st = {
            "phase": "idle",
            "sequence": list(seq),
            "total": int(len(seq)),
            "index": 0,
            "current_letter": str(seq[0] if seq else "a"),
            "hits": 0,
            "seconds_per_letter": float(spl),
            "time_left": float(spl),
            "feedback_time_left": 0.0,
        }
        S.typing_lab_state = st
        return dict(st)

    def typing_lab_press_key(key_text=""):
        st = getattr(S, "typing_lab_state", None)
        if not isinstance(st, dict):
            st = typing_lab_default_state()

        phase = str(st.get("phase", "idle") or "idle")
        if phase != "idle":
            return dict(st)

        got = str(key_text or "").strip().lower()[:1]
        if not ("a" <= got <= "z"):
            return dict(st)

        expected = str(st.get("current_letter", "") or "").lower()
        if got != expected:
            return dict(st)

        st["phase"] = "hit"
        st["hits"] = int(st.get("hits", 0) or 0) + 1
        st["feedback_time_left"] = 0.18
        S.typing_lab_state = st
        return dict(st)

    def typing_lab_tick(dt=0.02):
        st = getattr(S, "typing_lab_state", None)
        if not isinstance(st, dict):
            st = typing_lab_default_state()

        try:
            delta = float(dt)
        except:
            delta = 0.02
        if delta <= 0.0:
            delta = 0.02

        phase = str(st.get("phase", "idle") or "idle")

        if phase in ("hit", "timeout"):
            fb = float(st.get("feedback_time_left", 0.0) or 0.0)
            fb = max(0.0, fb - delta)
            st["feedback_time_left"] = fb
            S.typing_lab_state = st
            if fb <= 0.0:
                return typing_lab_advance()
            return dict(st)

        if phase != "idle":
            return dict(st)

        left = float(st.get("time_left", 0.0) or 0.0)
        left = max(0.0, left - delta)
        st["time_left"] = left

        if left <= 0.0:
            st["phase"] = "timeout"
            st["feedback_time_left"] = 0.20

        S.typing_lab_state = st
        return dict(st)

    def typing_lab_advance():
        st = getattr(S, "typing_lab_state", None)
        if not isinstance(st, dict):
            st = typing_lab_default_state()

        idx = int(st.get("index", 0) or 0) + 1
        seq = list(st.get("sequence", []) or [])
        total = int(st.get("total", len(seq)) or len(seq) or 0)
        spl = float(st.get("seconds_per_letter", 2.0) or 2.0)

        st["index"] = int(idx)

        if idx >= total:
            st["phase"] = "done"
            st["current_letter"] = ""
            st["time_left"] = 0.0
            st["feedback_time_left"] = 0.0
        else:
            st["phase"] = "idle"
            st["current_letter"] = str(seq[idx])
            st["time_left"] = float(spl)
            st["feedback_time_left"] = 0.0

        S.typing_lab_state = st
        return dict(st)

    store.typing_lab_default_state = typing_lab_default_state
    store.typing_lab_prepare = typing_lab_prepare
    store.typing_lab_press_key = typing_lab_press_key
    store.typing_lab_tick = typing_lab_tick
    store.typing_lab_advance = typing_lab_advance


default typing_lab_state = {
    "phase": "idle",
    "sequence": [],
    "total": 10,
    "index": 0,
    "current_letter": "",
    "hits": 0,
    "seconds_per_letter": 2.0,
    "time_left": 2.0,
    "feedback_time_left": 0.0,
}


screen typing_lab_qte_simple():
    modal True
    zorder 260

    default _letters = "abcdefghijklmnopqrstuvwxyz"

    python:
        _st = getattr(store, "typing_lab_state", {})
        _phase = str(_st.get("phase", "idle") or "idle")
        _cur = str(_st.get("current_letter", "") or "")
        _idx = int(_st.get("index", 0) or 0)
        _tot = int(_st.get("total", 10) or 10)
        _spl = float(_st.get("seconds_per_letter", 2.0) or 2.0)
        _left = float(_st.get("time_left", 0.0) or 0.0)
        _ratio = (0.0 if _spl <= 0.0 else max(0.0, min(1.0, _left / _spl)))
        _bar_max = 520
        _bar_fill = int(max(0, min(_bar_max, int(_bar_max * _ratio))))
        _timer_txt = ("%.2f" % float(_left))

        if _phase == "hit":
            _letter_color = "#66FF99"
        elif _phase == "timeout":
            _letter_color = "#FF4D4D"
        else:
            _letter_color = "#FFFFFF"

    timer 0.02 repeat True action Function(getattr(store, "typing_lab_tick", None), 0.02)

    for _k in _letters:
        key _k action Function(getattr(store, "typing_lab_press_key", None), _k)


    if _phase == "done":
        timer 0.02 action Return("win")

    add Solid("#000000")


    if _phase != "done":
        text (_cur if _cur else "-"):
            xalign 0.5
            yalign 0.48
            size 140
            bold True
            color _letter_color

        frame:
            background "#1A1A1A"
            xalign 0.5
            yalign 0.70
            xsize 540
            ysize 30
            padding (0, 0)

            fixed:
                xsize 540
                ysize 30

                frame:
                    background "#43E97B"
                    xpos 10
                    ypos 6
                    xsize _bar_fill
                    ysize 18
                    padding (0, 0)

        text ("Tiempo: " + _timer_txt + " s"):
            xalign 0.5
            yalign 0.76
            size 28
            color "#D0D0D0"

        text ("Letra %d/%d" % (int(min(_idx + 1, max(1, _tot))), int(max(1, _tot)))):
            xalign 0.5
            yalign 0.82
            size 30
            color "#D0D0D0"

screen typing_lab_win_popup():
    modal True
    zorder 270

    add Solid("#000000")

    frame:
        background "#0000"
        xalign 0.5
        yalign 0.5
        padding (24, 20)

        vbox:
            spacing 18

            text "GANASTE":
                size 78
                bold True
                color "#66FF99"
                xalign 0.5

            textbutton "Volver al menú":
                xalign 0.5
                action Return("menu")

label typing_lab_start:
    $ typing_lab_state = typing_lab_default_state()
    $ typing_lab_prepare(total_letters=10, seconds_per_letter=2.0)

label typing_lab_round:
    $ _typing_lab_simple_result = renpy.call_screen("typing_lab_qte_simple")
    if _typing_lab_simple_result != "win":
        jump typing_lab_round

    $ _typing_lab_popup_action = renpy.call_screen("typing_lab_win_popup")
    return

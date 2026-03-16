# Typing Lab aislado:
# - Fondo negro
# - Secuencia de 10 letras (a-z)
# - Sin timing y sin perder
# - Cada acierto pone la letra en verde, la oculta y aparece la siguiente con fade

init -850 python:
    import random
    import renpy.store as S

    def typing_lab_default_state():
        return {
            "phase": "idle",         # idle | hit | done
            "sequence": [],
            "total": 10,
            "index": 0,
            "current_letter": "",
            "hits": 0,
        }

    def typing_lab_prepare(total_letters=10):
        letters = list("abcdefghijklmnopqrstuvwxyz")
        try:
            n = int(total_letters)
        except:
            n = 10
        n = max(1, n)

        seq = [random.choice(letters) for _ in range(n)]

        st = {
            "phase": "idle",
            "sequence": list(seq),
            "total": int(len(seq)),
            "index": 0,
            "current_letter": str(seq[0] if seq else "a"),
            "hits": 0,
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
        S.typing_lab_state = st
        return dict(st)

    def typing_lab_advance():
        st = getattr(S, "typing_lab_state", None)
        if not isinstance(st, dict):
            st = typing_lab_default_state()

        idx = int(st.get("index", 0) or 0) + 1
        seq = list(st.get("sequence", []) or [])
        total = int(st.get("total", len(seq)) or len(seq) or 0)

        st["index"] = int(idx)

        if idx >= total:
            st["phase"] = "done"
            st["current_letter"] = ""
        else:
            st["phase"] = "idle"
            st["current_letter"] = str(seq[idx])

        S.typing_lab_state = st
        return dict(st)

    store.typing_lab_default_state = typing_lab_default_state
    store.typing_lab_prepare = typing_lab_prepare
    store.typing_lab_press_key = typing_lab_press_key
    store.typing_lab_advance = typing_lab_advance


default typing_lab_state = {
    "phase": "idle",
    "sequence": [],
    "total": 10,
    "index": 0,
    "current_letter": "",
    "hits": 0,
}

transform typing_lab_letter_fade:
    alpha 0.0
    linear 0.18 alpha 1.0


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
        _letter_color = ("#66FF99" if _phase == "hit" else "#FFFFFF")

    for _k in _letters:
        key _k action Function(getattr(store, "typing_lab_press_key", None), _k)

    if _phase == "hit":
        timer 0.18 action Function(getattr(store, "typing_lab_advance", None))

    if _phase == "done":
        timer 0.02 action Return("win")

    add Solid("#000000")

    # Evita que teclas globales cierren la screen y retornen al label por accidente.
    key "dismiss" action NullAction()
    key "game_menu" action NullAction()

    if _phase != "done":
        text (_cur if _cur else "-"):
            xalign 0.5
            yalign 0.5
            size 140
            bold True
            color _letter_color
            at typing_lab_letter_fade

        text ("Letra %d/%d" % (int(min(_idx + 1, max(1, _tot))), int(max(1, _tot)))):
            xalign 0.5
            yalign 0.80
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
    $ typing_lab_prepare(total_letters=10)

label typing_lab_round:
    $ _typing_lab_simple_result = renpy.call_screen("typing_lab_qte_simple")
    if _typing_lab_simple_result != "win":
        jump typing_lab_round

    $ _typing_lab_popup_action = renpy.call_screen("typing_lab_win_popup")
    return

# Minijuego aislado para practicar parry por tipeo.

screen typing_lab_result(_result=None):
    modal True
    zorder 260

    python:
        _r = _result if isinstance(_result, dict) else {}
        _hits = int(_r.get("hits", _r.get("typed_count", 0)) or 0)
        _misses = int(_r.get("misses", 0) or 0)
        _req = int(_r.get("required_hits", 6) or 6)
        _tot = int(_r.get("total_letters", 10) or 10)
        _ok = bool(_r.get("success", False))
        _executed = bool(_r.get("executed", True))
        _reason = str(_r.get("reason", "") or "")

    add Solid("#000000")

    frame:
        background "#0000"
        xalign 0.5
        yalign 0.5
        padding (24, 20)

        vbox:
            spacing 16

            text (("GANASTE" if _ok else "PERDISTE") if _executed else "INTERRUMPIDO"):
                size 72
                bold True
                color ("#66FF99" if _ok else "#FF4D4D") if _executed else "#FFCC66"
                xalign 0.5

            text ("Resultado final: ✔ %d / ✖ %d · mínimo %d de %d" % (_hits, _misses, _req, _tot)):
                size 28
                color "#DDDDDD"
                xalign 0.5

            if (not _executed) and _reason:
                text ("Motivo: %s" % _reason):
                    size 20
                    color "#BBBBBB"
                    xalign 0.5

            hbox:
                spacing 18
                xalign 0.5

                textbutton "Reintentar":
                    action [Hide("typing_lab_result"), Jump("typing_lab_start")]

                textbutton "Volver al menú":
                    action [Hide("typing_lab_result"), MainMenu()]

label typing_lab_start:
    # Flujo aislado: evita el resolver de combate (quiet UI + reintentos de capa)
    # para que el minijuego de práctica no cierre por interacciones externas.
    $ bs_counterattack_typing_prepare(count=10, seconds_per_letter=2.0, allow_repeat=True)
    $ _typing_lab_result = renpy.call_screen("counterattack_typing_qte")
    if not isinstance(_typing_lab_result, dict):
        $ _typing_lab_st = getattr(store, "counterattack_typing_state", {})
        if isinstance(_typing_lab_st, dict) and isinstance(_typing_lab_st.get("result"), dict):
            $ _typing_lab_result = dict(_typing_lab_st.get("result") or {})
        else:
            $ _typing_lab_result = {"executed": False, "success": False, "reason": "ui_closed_unexpectedly", "hits": 0, "misses": 0, "required_hits": 6, "total_letters": 10}
    call screen typing_lab_result(_typing_lab_result)
    return

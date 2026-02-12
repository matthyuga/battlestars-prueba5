# ===========================================================
# 00B_BATTLE_TURN_SUMMARY_OVERLAY.rpy – Placeholder/Overlay
# v0.1 Safe Placeholder
# ===========================================================

default last_turn_hits = 0
default last_turn_damage = 0

# Si después tu core define otros nombres, los adaptamos.
screen battle_turn_summary_overlay():
    zorder 120
    modal False

    # Placeholder invisible por defecto
    # (Si querés verlo, cambiá a True)
    $ _debug_show = False

    if _debug_show:
        frame:
            background "#0008"
            xalign 0.5
            yalign 0.02
            xpadding 12
            ypadding 8
            text "TURN SUMMARY (placeholder)" color "#FFFFFF" size 18
    else:
        null

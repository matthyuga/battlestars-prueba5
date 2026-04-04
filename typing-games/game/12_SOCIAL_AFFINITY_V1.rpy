# Sistema social de afinidad por barras (0..10)
# Fase 3: estado persistente + eventos de suma

init -110 python:
    import renpy.store as S

    AFFINITY_MAX = 10
    AFFINITY_MIN = 0

    AFFINITY_CHARACTER_IDS = [
        "airi", "momoka", "rinka", "sora",
        "aki", "ren", "tetsu",
        "misaki", "ayame", "kaoru",
        "haru", "yuto", "masato",
    ]

    AFFINITY_EVENT_VALUES = {
        "interaction_success": 1,
        "social_mission_success": 1,
    }

    def affinity_default_points():
        return {cid: 0 for cid in AFFINITY_CHARACTER_IDS}

    def _normalize_character_id(character_id):
        return str(character_id or "").strip().lower()

    def _affinity_clamp(value):
        try:
            iv = int(value)
        except:
            iv = 0
        return max(AFFINITY_MIN, min(AFFINITY_MAX, iv))

    def _affinity_ensure_store():
        current = getattr(S, "affinity_points", None)
        if not isinstance(current, dict):
            S.affinity_points = affinity_default_points()
            return S.affinity_points

        for cid in AFFINITY_CHARACTER_IDS:
            current[cid] = _affinity_clamp(current.get(cid, 0))

        S.affinity_points = current
        return current

    def get_affinity(character_id):
        st = _affinity_ensure_store()
        cid = _normalize_character_id(character_id)
        return int(st.get(cid, 0))

    def add_affinity(character_id, amount=1):
        """Suma afinidad por personaje con clamp 0..10."""
        st = _affinity_ensure_store()
        cid = _normalize_character_id(character_id)
        if cid not in st:
            st[cid] = 0

        try:
            delta = int(amount)
        except:
            delta = 0

        st[cid] = _affinity_clamp(st.get(cid, 0) + delta)
        S.affinity_points = st
        return int(st[cid])

    def award_affinity_event(character_id, event_key):
        """Eventos sociales de Fase 3:
        - interaction_success
        - social_mission_success
        """
        key = str(event_key or "").strip().lower()
        delta = int(AFFINITY_EVENT_VALUES.get(key, 0))
        return add_affinity(character_id, delta)

    def get_affinity_bar_image(character_id):
        points = get_affinity(character_id)
        return "gui/barra-progreso/c%d.png" % _affinity_clamp(points)


default affinity_points = affinity_default_points()

# Sistema de romance opcional (modo 3 + elegibilidad)
# Fase 4: enablement + puntos persistentes

init -100 python:
    import renpy.store as S

    ROMANCE_MIN = 0
    ROMANCE_MAX = 24  # hoy

    ROMANCE_CHARACTER_GENDER = {
        "airi": "female",
        "momoka": "female",
        "rinka": "female",
        "sora": "female",
        "misaki": "female",
        "ayame": "female",
        "kaoru": "female",
        "aki": "male",
        "ren": "male",
        "tetsu": "male",
        "haru": "male",
        "yuto": "male",
        "masato": "male",
    }

    def romance_default_points():
        return {cid: 0 for cid in ROMANCE_CHARACTER_GENDER.keys()}

    def _normalize_gender(gender):
        return str(gender or "").strip().lower()

    def _normalize_character_id(character_id):
        return str(character_id or "").strip().lower()

    def _romance_clamp(value):
        try:
            iv = int(value)
        except:
            iv = 0
        return max(ROMANCE_MIN, min(ROMANCE_MAX, iv))

    def _romance_ensure_store():
        current = getattr(S, "romance_points", None)
        if not isinstance(current, dict):
            S.romance_points = romance_default_points()
            return S.romance_points

        for cid in ROMANCE_CHARACTER_GENDER.keys():
            current[cid] = _romance_clamp(current.get(cid, 0))

        S.romance_points = current
        return current

    def is_romance_enabled(player_mode, player_gender, character_id):
        """Regla Fase 4:
        - Solo modo 3.
        - Solo personaje de sexo opuesto al del jugador.
        """
        try:
            mode = int(player_mode)
        except:
            mode = 1

        if mode != 3:
            return False

        pg = _normalize_gender(player_gender)
        if pg not in ("male", "female"):
            return False

        cid = _normalize_character_id(character_id)
        char_gender = _normalize_gender(ROMANCE_CHARACTER_GENDER.get(cid, ""))
        if char_gender not in ("male", "female"):
            return False

        return (pg == "male" and char_gender == "female") or (pg == "female" and char_gender == "male")

    def get_romance(character_id):
        st = _romance_ensure_store()
        cid = _normalize_character_id(character_id)
        return int(st.get(cid, 0))

    def add_romance(character_id, amount=1):
        """Suma romance por personaje con clamp 0..24 (hoy)."""
        st = _romance_ensure_store()
        cid = _normalize_character_id(character_id)
        if cid not in st:
            st[cid] = 0

        try:
            delta = int(amount)
        except:
            delta = 0

        st[cid] = _romance_clamp(st.get(cid, 0) + delta)
        S.romance_points = st
        return int(st[cid])


default romance_points = romance_default_points()

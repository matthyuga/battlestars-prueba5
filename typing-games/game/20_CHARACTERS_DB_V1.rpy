# ===========================================================
# 20_CHARACTERS_DB_V1.rpy
# Capa de Data (Fase 1A): personajes para motor académico/social
# ===========================================================

init -130 python:
    CHARACTER_DB_V1 = {
        "teachers": {
            "haru": {
                "id": "haru",
                "display_name": "Haru",
                "role": "teacher",
                "gender": "male",
                "portrait_primary": "gui/characters-sakura-sunshine/male/teachers/Haru.png",
                "portrait_fallback": "gui/characters-sakura-sunshine/female/teachers/Ayame.png",
                "missions": [],
                "affinity_hooks": [],
                "romance_hooks": [],
            },
            "misaki": {
                "id": "misaki",
                "display_name": "Misaki",
                "role": "teacher",
                "gender": "female",
                "portrait_primary": "gui/characters-sakura-sunshine/female/teachers/Misaki.png",
                "portrait_fallback": "gui/characters-sakura-sunshine/male/teachers/Masato.png",
                "missions": [],
                "affinity_hooks": [],
                "romance_hooks": [],
            },
            "ayame": {
                "id": "ayame",
                "display_name": "Ayame",
                "role": "teacher",
                "gender": "female",
                "portrait_primary": "gui/characters-sakura-sunshine/female/teachers/Ayame.png",
                "portrait_fallback": "gui/characters-sakura-sunshine/female/teachers/Ayame.png",
                "missions": [],
                "affinity_hooks": [],
                "romance_hooks": [],
            },
            "masato": {
                "id": "masato",
                "display_name": "Masato",
                "role": "teacher",
                "gender": "male",
                "portrait_primary": "gui/characters-sakura-sunshine/male/teachers/Masato.png",
                "portrait_fallback": "gui/characters-sakura-sunshine/male/teachers/Masato.png",
                "missions": [],
                "affinity_hooks": [],
                "romance_hooks": [],
            },
        },
        "companions": {
            "airi": {
                "id": "airi",
                "display_name": "Airi",
                "role": "companion",
                "gender": "female",
                "portrait_primary": "",
                "portrait_fallback": "",
                "missions": [],
                "affinity_hooks": [],
                "romance_hooks": [],
            },
            "momoka": {"id": "momoka", "display_name": "Momoka", "role": "companion", "gender": "female", "portrait_primary": "", "portrait_fallback": "", "missions": [], "affinity_hooks": [], "romance_hooks": []},
            "rinka": {"id": "rinka", "display_name": "Rinka", "role": "companion", "gender": "female", "portrait_primary": "", "portrait_fallback": "", "missions": [], "affinity_hooks": [], "romance_hooks": []},
            "sora": {"id": "sora", "display_name": "Sora", "role": "companion", "gender": "female", "portrait_primary": "", "portrait_fallback": "", "missions": [], "affinity_hooks": [], "romance_hooks": []},
            "aki": {"id": "aki", "display_name": "Aki", "role": "companion", "gender": "male", "portrait_primary": "", "portrait_fallback": "", "missions": [], "affinity_hooks": [], "romance_hooks": []},
            "ren": {"id": "ren", "display_name": "Ren", "role": "companion", "gender": "male", "portrait_primary": "", "portrait_fallback": "", "missions": [], "affinity_hooks": [], "romance_hooks": []},
            "tetsu": {"id": "tetsu", "display_name": "Tetsu", "role": "companion", "gender": "male", "portrait_primary": "", "portrait_fallback": "", "missions": [], "affinity_hooks": [], "romance_hooks": []},
            "kaoru": {"id": "kaoru", "display_name": "Kaoru", "role": "companion", "gender": "female", "portrait_primary": "", "portrait_fallback": "", "missions": [], "affinity_hooks": [], "romance_hooks": []},
            "yuto": {"id": "yuto", "display_name": "Yuto", "role": "companion", "gender": "male", "portrait_primary": "", "portrait_fallback": "", "missions": [], "affinity_hooks": [], "romance_hooks": []},
        },
    }

    def character_db_get(character_id, category=None):
        cid = str(character_id or "").strip().lower()
        if category in ("teachers", "companions"):
            table = CHARACTER_DB_V1.get(category, {})
            return dict(table.get(cid, {}))

        for section in ("teachers", "companions"):
            record = CHARACTER_DB_V1.get(section, {}).get(cid)
            if isinstance(record, dict):
                return dict(record)
        return {}

    def character_db_ids_by_role(role=None, gender=None):
        role_norm = str(role or "").strip().lower()
        gender_norm = str(gender or "").strip().lower()
        out = []

        for section in ("teachers", "companions"):
            for cid, record in CHARACTER_DB_V1.get(section, {}).items():
                if not isinstance(record, dict):
                    continue
                if role_norm and str(record.get("role", "")).lower() != role_norm:
                    continue
                if gender_norm and str(record.get("gender", "")).lower() != gender_norm:
                    continue
                out.append(cid)
        return out


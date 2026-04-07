# ===========================================================
# 30_LESSON_ENGINE_V1.rpy
# Capa de Engine/Lógica (Fase 2A)
# ===========================================================

init -115 python:
    import renpy.store as S

    def _lesson_safe_int(value, fallback=0):
        try:
            return int(value)
        except:
            return int(fallback)

    def lesson_get_sublesson_meta(sublesson_id, lesson_id="lesson_1"):
        """Devuelve metadata declarativa de una sublección."""
        sid = str(sublesson_id or "").strip().lower()
        lid = str(lesson_id or "lesson_1").strip().lower()
        if len(sid) == 0:
            return {}

        sub = lesson_db_get_sublesson(lid, sid) if "lesson_db_get_sublesson" in globals() else {}
        if not isinstance(sub, dict):
            return {}

        meta = dict(sub)
        meta.setdefault("id", sid)
        meta.setdefault("title", sid)
        meta.setdefault("state", "placeholder")
        meta.setdefault("scene_type", "placeholder")
        meta.setdefault("objective", "Contenido temporal.")
        steps = meta.get("steps", [])
        meta["steps"] = list(steps) if isinstance(steps, (list, tuple)) else []
        return meta

    def lesson_get_segment(sublesson_id, step, lesson_id="lesson_1"):
        """Devuelve un tramo/segmento de la sublección para UI por pasos."""
        meta = lesson_get_sublesson_meta(sublesson_id, lesson_id=lesson_id)
        steps = meta.get("steps", [])
        if len(steps) == 0:
            return {}

        idx = _lesson_safe_int(step, 0)
        if idx < 0:
            idx = 0
        if idx >= len(steps):
            idx = len(steps) - 1

        seg = steps[idx]
        return dict(seg) if isinstance(seg, dict) else {}

    def lesson_can_advance(sublesson_id, step, lesson_id="lesson_1"):
        """Indica si existe un siguiente tramo en la sublección."""
        meta = lesson_get_sublesson_meta(sublesson_id, lesson_id=lesson_id)
        steps = meta.get("steps", [])
        if len(steps) == 0:
            return False
        idx = _lesson_safe_int(step, 0)
        return idx < (len(steps) - 1)

    def lesson_complete(sublesson_id, lesson_id="lesson_1", module_id="clases"):
        """Registra la sublección como completada en checks académicos."""
        sid = str(sublesson_id or "").strip().lower()
        lid = str(lesson_id or "lesson_1").strip().lower()
        mid = str(module_id or "clases").strip().lower()
        if len(sid) == 0:
            return False

        if hasattr(S, "set_check"):
            try:
                S.set_check(mid, lid, sid, True)
                return True
            except:
                return False

        if "set_check" in globals():
            try:
                set_check(mid, lid, sid, True)
                return True
            except:
                return False
        return False


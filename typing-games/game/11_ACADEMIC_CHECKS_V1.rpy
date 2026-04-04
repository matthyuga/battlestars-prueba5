# Sistema académico por checks (sin barras)
# Fase 2: estructura + helpers de progreso

init -120 python:
    import renpy.store as S

    ACADEMIC_MODULE_BLUEPRINT = {
        "clases": {
            "lesson_1": [
                "1_1_intro",
                "1_2_home_row",
                "1_3_results",
                "1_4_keys_exercise",
                "1_5_exam_help",
                "1_6_words_exercise",
                "1_7_phrases_exercise",
            ],
        },
        "practica": {
            "practice_1": ["free_letters", "free_words", "free_phrases"],
        },
        "examenes": {
            "exam_1": ["attempt_1"],
        },
        "actividades": {
            "activity_1": ["quest_1"],
        },
        "diario": {
            "diary_1": ["view_summary"],
        },
        "biblioteca": {
            "library_1": ["open_index"],
        },
    }

    ACADEMIC_MODULE_ALIASES = {
        "clases": "clases",
        "practica": "practica",
        "práctica": "practica",
        "examenes": "examenes",
        "exámenes": "examenes",
        "actividades": "actividades",
        "diario": "diario",
        "biblioteca": "biblioteca",
    }

    def _academic_normalize_module(module_id=None):
        mid = str(module_id or "").strip().lower()
        return ACADEMIC_MODULE_ALIASES.get(mid, mid)

    def academic_default_checks():
        data = {}
        for module_id, lessons in ACADEMIC_MODULE_BLUEPRINT.items():
            data[module_id] = {}
            for lesson_id, steps in lessons.items():
                data[module_id][lesson_id] = {}
                for step_id in steps:
                    data[module_id][lesson_id][step_id] = False
        return data

    def _academic_ensure_store():
        current = getattr(S, "academic_checks", None)
        if not isinstance(current, dict):
            S.academic_checks = academic_default_checks()
            return S.academic_checks

        # Migra/agrega claves faltantes sin romper saves previos
        for module_id, lessons in ACADEMIC_MODULE_BLUEPRINT.items():
            if module_id not in current or not isinstance(current.get(module_id), dict):
                current[module_id] = {}
            for lesson_id, steps in lessons.items():
                if lesson_id not in current[module_id] or not isinstance(current[module_id].get(lesson_id), dict):
                    current[module_id][lesson_id] = {}
                for step_id in steps:
                    if step_id not in current[module_id][lesson_id]:
                        current[module_id][lesson_id][step_id] = False
        S.academic_checks = current
        return current

    def set_check(module_id, lesson_id, step_id, value=True):
        """Marca/desmarca checks académicos por módulo > lección > sublección."""
        module_key = _academic_normalize_module(module_id)
        lesson_key = str(lesson_id or "").strip().lower()
        step_key = str(step_id or "").strip().lower()
        st = _academic_ensure_store()

        if module_key not in st:
            st[module_key] = {}
        if lesson_key not in st[module_key]:
            st[module_key][lesson_key] = {}
        st[module_key][lesson_key][step_key] = bool(value)

        S.academic_checks = st
        return bool(st[module_key][lesson_key][step_key])

    def get_check(module_id, lesson_id, step_id):
        module_key = _academic_normalize_module(module_id)
        lesson_key = str(lesson_id or "").strip().lower()
        step_key = str(step_id or "").strip().lower()
        st = _academic_ensure_store()
        return bool(st.get(module_key, {}).get(lesson_key, {}).get(step_key, False))

    def get_check_progress(module_id):
        """Retorna avance por módulo para UI: total, completados y ratio."""
        module_key = _academic_normalize_module(module_id)
        st = _academic_ensure_store()
        lessons = st.get(module_key, {})

        total_steps = 0
        completed_steps = 0
        lesson_totals = {}

        for lesson_id, steps in lessons.items():
            if not isinstance(steps, dict):
                continue
            lesson_total = 0
            lesson_done = 0
            for _step_id, done in steps.items():
                lesson_total += 1
                if bool(done):
                    lesson_done += 1
            lesson_totals[lesson_id] = {
                "done": lesson_done,
                "total": lesson_total,
            }
            total_steps += lesson_total
            completed_steps += lesson_done

        ratio = (float(completed_steps) / float(total_steps)) if total_steps > 0 else 0.0

        return {
            "module": module_key,
            "done": int(completed_steps),
            "total": int(total_steps),
            "ratio": float(ratio),
            "lessons": lesson_totals,
        }


default academic_checks = academic_default_checks()

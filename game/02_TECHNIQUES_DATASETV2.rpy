# ============================================================
# 02_BATTLE_TECHNIQUES_DATASET.RPY – Catálogo de Técnicas
# ============================================================
# Versión v8.3 – NO Legacy Block + AliasSafe + StrongAttack Removed
# ------------------------------------------------------------
# ✔ Cada técnica tiene "id"
# ✔ "special": focus / boost en especiales
# ✔ strong_attack REMOVIDO (no existe más)
# ✔ Aliases IA defensivos SIN dict compartido (copia shallow)
# ✔ Validación fuerte (id/type/special/alias references)
# ✔ Reset usado por tipo
# ============================================================

init -991 python:

    # ------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------
    def _shallow_copy(d):
        try:
            return dict(d)
        except:
            return {} if d is None else {"_raw": d}

    _VALID_TYPES = ("offensive", "defensive", "special")

    battle_techniques = {

        # =======================================================
        # 🗡️ TÉCNICAS OFENSIVAS (MODERNAS)
        # =======================================================

        "extra_attack": {
            "id": "extra_attack",
            "name": "Ataque extra",
            "type": "offensive",
            "bonus_actions": 1,
            "used": False,
            "description": "Ataque rápido que permite una acción adicional."
        },

        "extra_tech": {
            "id": "extra_tech",
            "name": "Técnica extra",
            "type": "offensive",
            "bonus_actions": 1,
            "used": False,
            "description": "Permite ejecutar una técnica ofensiva adicional."
        },

        "stronger_attack": {
            "id": "stronger_attack",
            "name": "Ataque más fuerte",
            "type": "offensive",
            "bonus_actions": 0,
            "used": False,
            "description": "Un ataque devastador sin finalizar el turno."
        },

        "attack_reducer": {
            "id": "attack_reducer",
            "name": "Ataque reductor",
            "type": "offensive",
            "bonus_actions": 0,
            "defense_reduction": 0.10,
            "debuff": True,
            "used": False,
            "description": "Inflige daño y reduce un 10% las defensas enemigas."
        },

        "direct_attack": {
            "id": "direct_attack",
            "name": "Ataque directo",
            "type": "offensive",
            "special": "direct",
            "bonus_actions": 0,
            "used": False,
            "description": "Puede volverse indefendible si logra 2/3 éxitos en los dados."
        },

        "noatk_attack": {
            "id": "noatk_attack",
            "name": "Ataque negador",
            "type": "offensive",
            "special": "noatk",
            "bonus_actions": 0,
            "used": False,
            "description": "Si logra 2/3 éxitos, impide el ataque enemigo."
        },


        # =======================================================
        # ✨ TÉCNICAS ESPECIALES
        # =======================================================

        "focus": {
            "id": "focus",
            "name": "Concentrar",
            "type": "special",
            "special": "focus",
            "used": False,
            "description": "Duplica el poder de la próxima técnica aplicable."
        },

        "defense_boost": {
            "id": "defense_boost",
            "name": "Potenciar",
            "type": "special",
            "special": "boost",
            "used": False,
            "description": "Duplica la potencia de la próxima defensa."
        },


        # =======================================================
        # 🛡️ TÉCNICAS DEFENSIVAS (MODERNAS)
        # =======================================================

        "defense_extra": {
            "id": "defense_extra",
            "name": "Defensa extra",
            "type": "defensive",
            "bonus_actions": 1,
            "attack_reflect": 0.0,
            "attack_reduction": 0.0,
            "used": False,
            "description": "Permite bloquear daño y otorga una acción adicional."
        },

        "defense_reducer": {
            "id": "defense_reducer",
            "name": "Defensa reductora",
            "type": "defensive",
            "attack_reflect": 0.0,
            "attack_reduction": 0.10,
            "debuff": True,
            "used": False,
            "description": "Bloquea daño y reduce un 10% el ataque enemigo."
        },

        "defense_reflect": {
            "id": "defense_reflect",
            "name": "Defensa reflectora",
            "type": "defensive",
            "attack_reflect": 0.10,
            "reflective": True,
            "used": False,
            "description": "Bloquea daño y devuelve el 10% al enemigo."
        },

        "defense_strong_block": {
            "id": "defense_strong_block",
            "name": "Defensa fuerte",
            "type": "defensive",
            "used": False,
            "description": "Una defensa sólida de alto rendimiento."
        },
    }


    # =======================================================
    # IA DEFENSIVA — Alias (SIN dict compartido)
    # =======================================================
    battle_techniques.update({
        "def_extra":   _shallow_copy(battle_techniques["defense_extra"]),
        "def_reduct":  _shallow_copy(battle_techniques["defense_reducer"]),
        "def_reflect": _shallow_copy(battle_techniques["defense_reflect"]),
    })

    battle_techniques["def_extra"]["id"]   = "defense_extra"
    battle_techniques["def_reduct"]["id"]  = "defense_reducer"
    battle_techniques["def_reflect"]["id"] = "defense_reflect"
    battle_techniques["def_extra"]["alias_of"]   = "defense_extra"
    battle_techniques["def_reduct"]["alias_of"]  = "defense_reducer"
    battle_techniques["def_reflect"]["alias_of"] = "defense_reflect"


    # =======================================================
    # VALIDACIÓN FUERTE
    # =======================================================
    def battle_validate_techniques(show_log=False):

        required_modern = [
            "extra_attack", "extra_tech",
            "stronger_attack",
            "focus", "defense_boost",
            "attack_reducer", "direct_attack", "noatk_attack",
            "defense_reflect", "defense_extra", "defense_reducer",
            "defense_strong_block"
        ]

        missing = [k for k in required_modern if k not in battle_techniques]
        ok = (len(missing) == 0)

        problems = []

        for key, tech in battle_techniques.items():

            if not isinstance(tech, dict):
                problems.append("tech '{}' no es dict".format(key))
                continue

            tid = tech.get("id", None)
            if tid is None:
                problems.append("tech '{}' sin id".format(key))

            # coherencia id vs key para NO-alias
            if not tech.get("alias_of", None):
                if tid is not None and tid != key:
                    problems.append("tech '{}' id!='{}'".format(key, key))

            ttype = tech.get("type", None)
            if ttype not in _VALID_TYPES:
                problems.append("tech '{}' type inválido ({})".format(key, ttype))

            sp = tech.get("special", None)
            if sp is not None and sp not in ("focus", "boost", "direct", "noatk"):
                problems.append("tech '{}' special inválido ({})".format(key, sp))

            alias_of = tech.get("alias_of", None)
            if alias_of is not None and alias_of not in battle_techniques:
                problems.append("tech '{}' alias_of inexistente ({})".format(key, alias_of))

        ok = ok and (len(problems) == 0)

        if show_log:
            try:
                if ok:
                    renpy.say(None, "[CHECK] Técnicas válidas (dataset v8.3, sin legacy).")
                else:
                    msg = "[CHECK] Dataset con problemas:"
                    if missing:
                        msg += "\n - FALTAN: " + ", ".join(missing)
                    if problems:
                        msg += "\n - " + "\n - ".join(problems[:10])
                        if len(problems) > 10:
                            msg += "\n - (+{} más)".format(len(problems) - 10)
                    renpy.say(None, msg)
            except:
                pass

        return ok


    # =======================================================
    # RESET GENERAL DE TÉCNICAS
    # =======================================================
    def battle_reset_used_by_type(kind_list=None):
        for key, tech in battle_techniques.items():
            try:
                if (not kind_list) or (tech.get("type") in kind_list):
                    tech["used"] = False
            except:
                pass


    # Export opcional
    try:
        import renpy.store as S
        S.battle_techniques = battle_techniques
        S.battle_validate_techniques = battle_validate_techniques
        S.battle_reset_used_by_type = battle_reset_used_by_type
    except:
        pass

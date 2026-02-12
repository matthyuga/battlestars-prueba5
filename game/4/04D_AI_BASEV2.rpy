# ===========================================================
# 04D_AI_BASE.rpy – Clase base de IA + Subclases
# v2.1 Dataset Routing + StoreSafe Reset Edition
# -----------------------------------------------------------
# ✔ Base lista para dynamic-cost + final_value_factory (04X)
# ✔ Compatible con v12.x AI_EXECUTION (next_action + current_plan)
# ✔ Dataset real por enemigo: busca primero en ai.dataset, luego fallback a S.battle_techniques
# ✔ Reset_turn store-safe: limpia flags peligrosos del enemigo (FocusCost / focus drift)
# ✔ Preparado para IA avanzada (estilos, agresividad, etc.)
# ===========================================================

init -990 python:
    import renpy.store as S

    # =======================================================
    # 🧠 CLASE BASE DE IA
    # =======================================================
    class BattleAI(object):
        def __init__(self, name, dataset=None):
            """
            name    = nombre visual de la IA (Grimmjow, Nel…)
            dataset = dict de técnicas del enemigo (opcional).
                      Si es None, se usa fallback a S.battle_techniques.
            """
            self.name = name
            self.dataset = dataset

            # Cola de acciones planeadas (strings: "extra_attack", "focus", etc.)
            self.current_plan = []

            # Reservado para IA avanzada (no es source-of-truth del focus real)
            self.behavior_mode = "normal"   # otros: "aggressive", "defensive", "low_reiatsu"

            # Campo opcional para multiplicadores internos (si lo usás en el futuro)
            self.temp_multiplier = 1

        # ---------------------------------------------------
        # Resolver dataset real de técnicas (store-safe)
        # ---------------------------------------------------
        def _get_dataset(self):
            """
            Retorna el dict de técnicas a usar:
            - primero ai.dataset si es dict
            - si no, fallback a S.battle_techniques
            """
            if isinstance(self.dataset, dict) and self.dataset:
                return self.dataset
            return getattr(S, "battle_techniques", {}) or {}

        def get_tech(self, key, default=None):
            """
            Devuelve el dict de la técnica.
            Importante: busca primero en ai.dataset, luego fallback global.
            """
            ds = self._get_dataset()
            if default is None:
                default = {}
            try:
                return ds.get(key, default)
            except:
                return default

        def has_tech(self, key):
            """
            True si la técnica existe en el dataset efectivo.
            """
            ds = self._get_dataset()
            try:
                return key in ds
            except:
                return False

        # ---------------------------------------------------
        # Acción siguiente del plan
        # ---------------------------------------------------
        def next_action(self):
            """
            Retorna la key de la próxima acción o "none".
            """
            if self.current_plan:
                return self.current_plan.pop(0)
            return "none"

        # ---------------------------------------------------
        # Reinicio de turno (store-safe)
        # ---------------------------------------------------
        def reset_turn(self, actor="enemy"):
            """
            Limpia el estado interno de la IA + flags del store que pueden quedar colgados.
            actor: "enemy" o "player" (por si reutilizás IA)
            """
            self.current_plan = []
            self.behavior_mode = "normal"
            self.temp_multiplier = 1

            # -----------------------------
            # 🔒 Limpieza de flags en STORE
            # -----------------------------
            try:
                if actor == "enemy":
                    # FocusCost ofensivo pendiente (tu fix reciente)
                    if hasattr(S, "enemy_focus_cost_pending"):
                        S.enemy_focus_cost_pending = False

                    # Si existieran flags futuros similares, los limpiamos safe:
                    if hasattr(S, "enemy_focus_pending"):
                        S.enemy_focus_pending = False

                    # Si tu sistema usa niveles/contadores, evitamos drift:
                    if hasattr(S, "enemy_focus_level"):
                        S.enemy_focus_level = 0

                else:
                    if hasattr(S, "player_focus_cost_pending"):
                        S.player_focus_cost_pending = False
                    if hasattr(S, "player_focus_level"):
                        S.player_focus_level = 0
            except:
                pass


    # =======================================================
    # SUBCLASES – Personalidades
    # =======================================================
    class BattleAI_Grimmjow(BattleAI):
        """
        IA agresiva futura:
        - Podría priorizar stronger_attack si tiene mucho reiatsu
        - o usar focus doble antes de atacar
        """
        pass


    class BattleAI_Nel(BattleAI):
        """
        IA más equilibrada o defensiva.
        """
        pass


    class BattleAI_Hollow(BattleAI):
        """
        IA genérica para enemigos comunes.
        """
        pass

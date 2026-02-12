# ===========================================================
# 01_ACTION_MODEL.rpy
# Sistema profesional de Acciones del Jugador
# v1.2 – Focus Non-Stack + Safe Dependencies Edition
# -----------------------------------------------------------
# - Action representa una acción en la cola
# - Dependencias blindadas (battle_techniques / reiatsu_energy_base)
# - Focus NO acumula (no x2, x4, x8 por cola)
# - Focus aplica solo al turno/acción actual (x2 o x1)
# - Soporte futuro: tech flag energy_scales (True/False)
# ===========================================================

init -990 python:
    import renpy.store as S

    class Action:
        """
        Representa UNA acción en la cola.

        - name: nombre visual
        - tech_id: id real de técnica (None si es un "buff" tipo Focus/Potenciar)
        - index: posición en la cola (debug/UI)

        Importante:
        - "Focus" (Concentrar/Potenciar) NO se acumula en multiplicadores por cola.
          En vez de contar focos anteriores, el multiplicador sale del estado global del turno
          (ej: focus_off_current_mult / boost_def_current_mult) o de un flag que vos pases.
        """

        def __init__(self, name, tech_id, index):
            self.name = name
            self.tech_id = tech_id
            self.index = index

            # Tipo
            self.is_focus = (tech_id is None)
            self.is_offensive = False
            self.is_defensive = False

            # Flags por técnica (futuro)
            self.energy_scales = False  # si True, energía también escala con focus

            # Resolver tipo desde battle_techniques (blindado)
            if tech_id is not None:
                techniques = getattr(S, "battle_techniques", {})
                tech = techniques.get(tech_id, {}) if isinstance(techniques, dict) else {}
                t = tech.get("type")

                if t == "offensive":
                    self.is_offensive = True
                elif t == "defensive":
                    self.is_defensive = True

                # Flag futuro: si la técnica quiere que energía también escale
                self.energy_scales = bool(tech.get("energy_scales", False))

            # Valores base / finales
            self.base_value = 0
            self.final_value = 0

            # Costos base
            self.base_rei = 0
            self.base_ene = 0

            # Costos finales
            self.final_rei = 0
            self.final_ene = 0

            # Multiplicador del turno (no-stack)
            self.focus_multiplier = 1

        # ---------------------------------------------------
        # Carga de valores base desde REIATSU/ENERGY SYSTEM
        # ---------------------------------------------------
        def set_base_stats(self):
            """
            Carga valores base usando reiatsu_energy_base(tech_id).
            Blindado: si la función no existe o retorna vacío, usa defaults.
            """
            if self.tech_id is None:
                return

            base_fn = getattr(S, "reiatsu_energy_base", None)
            if not callable(base_fn):
                # No crashear: se queda en 0
                return

            base = base_fn(self.tech_id) or {}
            if not isinstance(base, dict):
                base = {}

            self.base_value = base.get("value", 0)
            self.base_rei   = base.get("reiatsu", 0)
            self.base_ene   = base.get("energy", 0)

        # ---------------------------------------------------
        # Determina multiplicador de Focus (NO acumulable)
        # ---------------------------------------------------
        def compute_focus_multiplier(self):
            """
            Focus NO se acumula por cola.

            Regla:
            - Si la acción es una técnica ofensiva y hay focus ofensivo activo -> x2
            - Si la acción es una técnica defensiva y hay boost defensivo activo -> x2
            - Caso contrario -> x1

            Esto depende de tu core:
            - focus_off_current_mult (para ofensivo)
            - boost_def_current_mult (para defensivo)

            Si no existen, default = 1.
            """
            mult = 1

            if self.tech_id is None:
                self.focus_multiplier = 1
                return

            if self.is_offensive:
                mult = getattr(S, "focus_off_current_mult", 1)
            elif self.is_defensive:
                mult = getattr(S, "boost_def_current_mult", 1)

            # Blindaje: solo permitir 1 o 2 (no-stack)
            self.focus_multiplier = 2 if int(mult) >= 2 else 1

        # ---------------------------------------------------
        # Calcula valor final y costos finales
        # ---------------------------------------------------
        def apply_multipliers(self):
            """
            Focus multiplica valor y Reiatsu.
            Energía solo se multiplica si la técnica tiene energy_scales=True.
            """
            if self.tech_id is None:
                # Focus como acción no tiene valor/costos directos
                self.final_value = 0
                self.final_rei = 0
                self.final_ene = 0
                return

            m = self.focus_multiplier

            # Valor final (daño / defensa)
            self.final_value = self.base_value * m

            # Costos finales
            self.final_rei = self.base_rei * m
            self.final_ene = (self.base_ene * m) if self.energy_scales else self.base_ene

        # ---------------------------------------------------
        # Helper: pipeline completo
        # ---------------------------------------------------
        def compute_all(self):
            """
            Conveniencia: calcula todo en orden correcto.
            """
            self.set_base_stats()
            self.compute_focus_multiplier()
            self.apply_multipliers()

        # ---------------------------------------------------
        # Representación para debugging
        # ---------------------------------------------------
        def to_debug_string(self):
            return "[{}] {} | tech_id={} | type={} | mult={} | val={} | rei={} | ene={}".format(
                self.index,
                self.name,
                self.tech_id,
                "OFF" if self.is_offensive else ("DEF" if self.is_defensive else "N/A"),
                self.focus_multiplier,
                self.final_value,
                self.final_rei,
                self.final_ene
            )

    # Exponer en store por consistencia
    S.Action = Action

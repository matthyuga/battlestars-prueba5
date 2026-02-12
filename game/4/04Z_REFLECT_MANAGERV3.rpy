# ============================================================
# 04Z_REFLECT_MANAGER.RPY – Sistema Unificado de Reflejo
# ============================================================
# Versión: v1.2.0 ReflectManager Target+Source FINAL
# Ren’Py 7.4.9 Compatible
# ------------------------------------------------------------
# ✔ Unifica reflejo jugador e IA
# ✔ Guarda reflect POR OBJETIVO (quién lo recibirá)
# ✔ Guarda FUENTE (quién lo generó) → debug panel correcto
# ✔ Consumir = borrar y devolver
# ✔ consume() legacy (solo valor)
# ✔ consume_info() moderno (valor + fuente)
# ✔ clear(id) / clear_all() seguros
# ✔ Engine-safe (NO importa renpy en init temprano)
# ✔ Compatible con defensive_resolve v11.4
# ============================================================

init -999 python:

    class ReflectManager(object):

        def __init__(self):
            # { target_id(str): int_value }
            self._values = {}

            # { target_id(str): source_id(str or None) }
            self._sources = {}

            self.debug = False
            self.max_value = None   # opcional clamp (None = sin límite)

        # ---------------------------------------------------
        # 🔧 Utils internos
        # ---------------------------------------------------
        def _norm_id(self, v):
            try:
                return str(v)
            except:
                return "unknown"

        def _to_int(self, v, default=0):
            try:
                return int(v)
            except:
                try:
                    return int(default)
                except:
                    return 0

        def _clamp(self, v):
            mv = self.max_value
            if mv is None:
                return v
            try:
                mv = int(mv)
            except:
                return v
            if mv <= 0:
                return v
            return min(v, mv)

        def _log(self, msg):
            if not self.debug:
                return
            try:
                import renpy
                renpy.log(msg)
            except:
                return

        # ---------------------------------------------------
        # ➕ Agregar reflect
        # target_id = quien lo RECIBIRÁ (atacante)
        # source_id = quien lo GENERÓ (defensor)
        # ---------------------------------------------------
        def add(self, target_id, value, source_id=None):
            t = self._norm_id(target_id)
            s = None if source_id is None else self._norm_id(source_id)

            v = self._to_int(value, 0)
            if v <= 0:
                return 0

            v = self._clamp(v)

            cur = self._to_int(self._values.get(t, 0), 0)
            total = self._clamp(cur + v)

            self._values[t] = total
            self._sources[t] = s  # última fuente válida

            self._log(
                "REFLECT.ADD target={} +{} => {} (source={})"
                .format(t, v, total, s)
            )

            return v

        # ---------------------------------------------------
        # 👀 Leer sin borrar
        # ---------------------------------------------------
        def get(self, target_id):
            t = self._norm_id(target_id)
            return self._to_int(self._values.get(t, 0), 0)

        def get_source(self, target_id):
            t = self._norm_id(target_id)
            return self._sources.get(t, None)

        # ---------------------------------------------------
        # 🔥 Consumir (LEGACY)
        # Devuelve SOLO el valor
        # ---------------------------------------------------
        def consume(self, target_id):
            t = self._norm_id(target_id)
            v = self._to_int(self._values.get(t, 0), 0)

            if v <= 0:
                return 0

            self._log(
                "REFLECT.CONSUME target={} value={} (source={})"
                .format(t, v, self._sources.get(t))
            )

            self._values.pop(t, None)
            self._sources.pop(t, None)
            return v

        # ---------------------------------------------------
        # 🔥 Consumir (MODERNO)
        # Devuelve (valor, fuente)
        # ---------------------------------------------------
        def consume_info(self, target_id):
            t = self._norm_id(target_id)
            v = self._to_int(self._values.get(t, 0), 0)

            if v <= 0:
                return 0, None

            s = self._sources.get(t, None)

            self._log(
                "REFLECT.CONSUME_INFO target={} value={} (source={})"
                .format(t, v, s)
            )

            self._values.pop(t, None)
            self._sources.pop(t, None)
            return v, s

        # ---------------------------------------------------
        # 🧹 Limpieza
        # ---------------------------------------------------
        def clear(self, target_id):
            t = self._norm_id(target_id)
            if t in self._values or t in self._sources:
                self._log("REFLECT.CLEAR target={}".format(t))
            self._values.pop(t, None)
            self._sources.pop(t, None)

        def clear_all(self):
            self._log("REFLECT.CLEAR_ALL")
            self._values = {}
            self._sources = {}

        # ---------------------------------------------------
        # 🐞 Debug
        # ---------------------------------------------------
        def dump(self, force=False):
            if not (self.debug or force):
                return
            try:
                import renpy
                renpy.log(
                    "REFLECT.DUMP values={} sources={}"
                    .format(self._values, self._sources)
                )
            except:
                return

        # ---------------------------------------------------
        # Helpers
        # ---------------------------------------------------
        def has(self, target_id):
            return self.get(target_id) > 0

        def set_debug(self, enabled=True):
            self.debug = bool(enabled)
            self._log("REFLECT.DEBUG -> {}".format(self.debug))


    # -------------------------------------------------------
    # 🌐 Instancia global
    # -------------------------------------------------------
    reflect = ReflectManager()

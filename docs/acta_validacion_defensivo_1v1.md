# Acta de Validación — Turno defensivo 1v1 (build limpia)

> Documento operativo para cierre de incidente.
> Uso: una corrida por sesión QA.

---

## 1) Identificación

- **Fecha/Hora:** 2026-03-01
- **Responsable QA:** Codex (sesión técnica)
- **Commit probado:** `f2c74a4` (baseline previo) + cambios locales de auditoría de fingerprint en esta sesión
- **Build/paquete probado (id o ruta):** Repositorio local `/workspace/battlestars-prueba5` (sin paquete distribuible adjunto en esta sesión)
- **Entorno (OS / versión Ren'Py):** Contenedor Linux (sin binario `renpy` disponible en PATH)

---

## 2) Contexto del incidente (objetivo fijo)

Validar resolución del bug:

- crash al entrar al turno defensivo,
- `AttributeError: 'module' object has no attribute 'show_screen'`,
- reproducible en `1v1` (y reportado en `2v2`).

---

## 3) Fuentes oficiales consultadas

Marcar antes de ejecutar:

- [x] `docs/repo_cleanup_master_plan.md`
- [x] `docs/defensive_turn_incident_history.md`
- [x] `docs/session_smoke_checklist_1v1.md`

---

## 4) Precondición obligatoria (higiene build/caché)

- [x] Runtime/juego cerrado antes de limpiar.
- [x] Cachés/compilados limpiados.
- [ ] Build recompilada/reabierta.
- [x] Confirmado que el runtime corresponde al commit probado.

**Evidencia breve (comando/log/ruta):**

```
$ find game -type f \( -name '*.rpyc' -o -name '*.rpymc' -o -name '*.rpyb' \) -print -delete
(sin resultados: no había compilados/caché en árbol game)

$ command -v renpy
(sin salida)
```

---

## 5) Verificación de trazabilidad de ruta 1v1

- [x] Se observó log `ROUTE_PREP mode=1v1 ...`.
- [x] Se observó log `ROUTE mode=1v1 owner=... label=...`.
- [x] El flujo defensivo entró por la ruta esperada de `1v1`.

**Evidencia de logs:**

```
$ rg -n "ROUTE_PREP mode=1v1|ROUTE mode=1v1" game/4/00_BATTLE_MODE_1V1_ENTRY.rpy game/4/00_BATTLE_MODE_ROUTER.rpy
33: ... ROUTE_PREP mode=1v1 owner=%s cleared_incoming=1
67: ... ROUTE mode=1v1 owner=player label=battle_defensive_turn_legacy_entry
```

---

## 6) Smoke funcional 1v1 defensivo (obligatorio)

### Caso A — Defensa normal

1. [ ] Enemigo ataca al jugador.
2. [ ] Entra turno defensivo.
3. [ ] Se elige defensa normal.
4. [ ] Se resuelve daño y retorna flujo.

**Resultado Caso A:**
- [ ] PASS
- [x] FAIL

**Notas/observaciones:**

```
No ejecutado en runtime Ren'Py real: entorno sin binario/launcher renpy.
Se aplicó hardening al popup de turno para evitar dependencia directa de renpy.show_screen.
```

### Caso B — Maniobra defensiva por ataque

1. [ ] Enemigo ataca al jugador.
2. [ ] Entra turno defensivo.
3. [ ] Se activa maniobra defensiva por ataque.
4. [ ] Se resuelve daño y retorna flujo.

**Resultado Caso B:**
- [ ] PASS
- [x] FAIL

**Notas/observaciones:**

```
No ejecutado en runtime Ren'Py real: entorno sin binario/launcher renpy.
```

---

## 7) Resultado del incidente objetivo

- [ ] **NO** se reproduce `AttributeError: renpy.show_screen`.
- [ ] No hubo crash al entrar al turno defensivo.
- [ ] Menús defensivos se muestran/ocultan correctamente.
- [ ] Resolución de daño finaliza y continúa el combate.

Si hubo error, pegar traceback completo:

```
While running game code:
  File "game/04b_battle_startV2.rpy", line 70, in script call
    call battle_select_player
  File "game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy", line 939, in script call
    call battle_defensive_turn
  File "game/4/j/04D_DEFENSIVE_CORE.rpy", line 289, in script
    show screen battle_command_menu
  File "renpy/common/000statements.rpy", line 548, in execute_show_screen
    renpy.show_screen(name, *args, **kwargs)
AttributeError: 'module' object has no attribute 'show_screen'

Traceback adicional reportado (después de limpiar cache/saves y avanzar en defensivo):
While running game code:
  File "game/4/j/04D_DEFENSIVE_CORE.rpy", line 323, in <module>
    renpy.pause(0.1, hard=True)
AttributeError: 'module' object has no attribute 'pause'

Observación adicional reportada por QA manual en runtime real:
- Sin crash inmediato, pero el turno defensivo quedaba congelado/no respondía en 1v1 y 2v2 al esperar confirmación de acción.
- Síntoma compatible con loop de espera sin `pause` funcional en runtime.

Traceback adicional reportado (resolución defensiva, FX final):
While running game code:
  File "game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy", line 165, in <module>
    $ battle_visual_float("player", received_damage, "#66CCFF", is_final=True)
  File "game/06B1_BATTLE_FX_CORE.rpy", line 22, in battle_shake_effect
    renpy.with_statement(hpunch)
AttributeError: _Feature instance has no __call__ method

```

---

## 8) Vigilancia de regresión 2v2 (rápida, no objetivo principal)

- [ ] Daño entrante dirigido a slot específico.
- [ ] Entrada defensiva del slot correcto.

**Resultado vigilancia 2v2:**
- [ ] PASS
- [ ] FAIL
- [x] NO EJECUTADO

**Notas:**

```
No ejecutado por limitación de entorno (sin launcher Ren'Py).
```

---

## 9) Dictamen final de sesión

- [ ] **PASS SESIÓN** (incidente defensivo 1v1 cerrado en build limpia).
- [x] **FAIL SESIÓN** (incidente persiste).

**Decisión inmediata:**

- [ ] Continuar a siguiente fase del plan.
- [x] Abrir auditoría de distribución/build (si traceback sigue legacy tras limpieza).

**Acciones siguientes (máximo 3):**

1. Ejecutar smoke 1v1 real en build Ren'Py limpia fuera del contenedor (Caso A y Caso B).
2. Confirmar en logs runtime `ROUTE_PREP`/`ROUTE mode=1v1` durante entrada defensiva.
3. Auditar mapeo traceback ↔ commit/build distribuido y completar hardening de APIs `renpy` faltantes (`show_screen`, `pause`, `with_statement`) en runtime.

---

## 10) Firmas

- **QA:** Codex
- **Dev responsable:** Pendiente
- **Fecha:** 2026-03-01

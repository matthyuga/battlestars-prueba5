# Acta de Validación — Turno defensivo 1v1 (build limpia)

> Documento operativo para cierre de incidente.
> Uso: una corrida por sesión QA.

---

## 1) Identificación

- **Fecha/Hora:**
- **Responsable QA:**
- **Commit probado:**
- **Build/paquete probado (id o ruta):**
- **Entorno (OS / versión Ren'Py):**

---

## 2) Contexto del incidente (objetivo fijo)

Validar resolución del bug:

- crash al entrar al turno defensivo,
- `AttributeError: 'module' object has no attribute 'show_screen'`,
- reproducible en `1v1` (y reportado en `2v2`).

---

## 3) Fuentes oficiales consultadas

Marcar antes de ejecutar:

- [ ] `docs/repo_cleanup_master_plan.md`
- [ ] `docs/defensive_turn_incident_history.md`
- [ ] `docs/session_smoke_checklist_1v1.md`

---

## 4) Precondición obligatoria (higiene build/caché)

- [ ] Runtime/juego cerrado antes de limpiar.
- [ ] Cachés/compilados limpiados.
- [ ] Build recompilada/reabierta.
- [ ] Confirmado que el runtime corresponde al commit probado.

**Evidencia breve (comando/log/ruta):**

```
<Pegar evidencia>
```

---

## 5) Verificación de trazabilidad de ruta 1v1

- [ ] Se observó log `ROUTE_PREP mode=1v1 ...`.
- [ ] Se observó log `ROUTE mode=1v1 owner=... label=...`.
- [ ] El flujo defensivo entró por la ruta esperada de `1v1`.

**Evidencia de logs:**

```
<Pegar líneas relevantes>
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
- [ ] FAIL

**Notas/observaciones:**

```
<Pegar notas>
```

### Caso B — Maniobra defensiva por ataque

1. [ ] Enemigo ataca al jugador.
2. [ ] Entra turno defensivo.
3. [ ] Se activa maniobra defensiva por ataque.
4. [ ] Se resuelve daño y retorna flujo.

**Resultado Caso B:**
- [ ] PASS
- [ ] FAIL

**Notas/observaciones:**

```
<Pegar notas>
```

---

## 7) Resultado del incidente objetivo

- [ ] **NO** se reproduce `AttributeError: renpy.show_screen`.
- [ ] No hubo crash al entrar al turno defensivo.
- [ ] Menús defensivos se muestran/ocultan correctamente.
- [ ] Resolución de daño finaliza y continúa el combate.

Si hubo error, pegar traceback completo:

```
<Pegar traceback>
```

---

## 8) Vigilancia de regresión 2v2 (rápida, no objetivo principal)

- [ ] Daño entrante dirigido a slot específico.
- [ ] Entrada defensiva del slot correcto.

**Resultado vigilancia 2v2:**
- [ ] PASS
- [ ] FAIL
- [ ] NO EJECUTADO

**Notas:**

```
<Pegar notas>
```

---

## 9) Dictamen final de sesión

- [ ] **PASS SESIÓN** (incidente defensivo 1v1 cerrado en build limpia).
- [ ] **FAIL SESIÓN** (incidente persiste).

**Decisión inmediata:**

- [ ] Continuar a siguiente fase del plan.
- [ ] Abrir auditoría de distribución/build (si traceback sigue legacy tras limpieza).

**Acciones siguientes (máximo 3):**

1.
2.
3.

---

## 10) Firmas

- **QA:**
- **Dev responsable:**
- **Fecha:**

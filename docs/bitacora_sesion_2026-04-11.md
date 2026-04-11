# Bitácora de sesión — Battlestars (11 abril 2026)

## Objetivo general de la sesión
Ordenar el rumbo de Battlestars Saga y dejar bases técnicas iniciales para economía, inventarios y progresión, mientras se corregían/ajustaban varios puntos de UI/HUD.

---

## Temas tratados (resumen ejecutivo)

### 1) Estabilidad de UI (iteraciones)
- Se abordaron varios ajustes visuales y de UX en combate:
  - input de nombre (modal y limpieza visual),
  - quick menu oculto en combate/pantallas específicas,
  - limpieza de textos tutoriales redundantes,
  - comportamiento del scrollbar en selector de técnicas,
  - HUD del jugador con retrato/nombre dinámico.

### 2) Panel de recompensas C4
- Se aclaró que el panel C4 pertenece al flujo de post-combate integrado con simulación.
- Se movió el botón de continuar dentro del panel (cabecera, arriba a la derecha) para mejor navegación.

### 3) Dirección de diseño del proyecto
- Se consolidó que, por ahora, el foco es **Battlestars Saga** con modos:
  - Duelo libre,
  - Torneos por tier (C/B/A),
  - Torre del cielo.
- Se reafirmó separación en dos capas:
  - progreso de cuenta,
  - progreso de héroe.

### 4) Reglas de inventario/economía definidas
- Regla clave acordada:
  - **el inventario del héroe no guarda oro**,
  - **el oro vive en inventario general de cuenta (baúl)**.

### 5) Implementación por fases
- Se acordó una ejecución incremental y se inició base de Fases 1–4:
  - Fase 1: canon de tipos + schemas mínimos,
  - Fase 2: economía/inventarios + transferencia baúl→héroe,
  - Fase 3: ruteo de recompensas por modo,
  - Fase 4: auditoría simple de economía (ingresos, transferencias, consumos).

---

## Artefactos/documentos creados o actualizados en la sesión
- `docs/battlestars_saga_rules_v1.md`
- `game/12E_SAGA_FOUNDATIONS_V1.rpy`

---

## Acuerdos de producto que quedan vigentes
1. Canon Saga (v1): `PLAYER/BETA/GAMMA`.
2. Cuenta y héroe son capas separadas.
3. Oro global de cuenta, nunca en inventario de héroe.
4. Torre del cielo es el modo donde progresa el héroe de forma más profunda.
5. Duelo/Torneo priorizan progresión de cuenta (con reglas específicas por modo).

---

## Próximo foco sugerido
Integrar el router de recompensas al flujo real de cierre de combate por modo (primero Duelo libre), y luego exponer UI de baúl/inventario de héroe para operar transferencias manuales.

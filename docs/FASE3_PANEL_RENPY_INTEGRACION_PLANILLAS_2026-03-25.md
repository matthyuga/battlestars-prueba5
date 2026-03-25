# Fase 3 — Integración de planillas en runtime (Ren'Py)

Fecha: 2026-03-25  
Estado: completada (caps + consumo conectados a UI/core).

## Alcance ejecutado

Se integraron planillas funcionalmente en runtime mediante el core/UI:

1. Core (`game/10A_RPG_PANEL_CORE_V1.rpy`):
   - Nuevo cálculo `compute_consumption_at_cap(register, mode)`.
   - Implementación de curvas de energía por familia de técnica:
     - escala 9
     - técnica extra
     - reductor
     - directo/negador
     - reflectora
     - efecto especial
   - Salida estructurada para ofensiva y defensiva (cap, reiatsu y energía por familia).

2. UI (`game/10B_RPG_PANEL_UI_V1.rpy`):
   - Visualización de consumo al cap por modo/tier actual.
   - Bloque explícito “Consumo al cap (integración Fase 3)”
   - Datos de ofensiva y defensiva mostrados en tiempo real con `compute_consumption_at_cap`.

## Criterio de fase cubierto

- La pantalla dejó de usar números mock para consumo y ahora deriva de funciones sincronizadas con planillas de diseño.

## Nota

La integración de recompensas post-combate (EXP/Oro por ΔR + desempeño + anti-abuso) permanece para Fase 4.

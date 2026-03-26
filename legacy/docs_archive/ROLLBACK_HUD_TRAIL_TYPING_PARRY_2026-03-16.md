# Registro de rollback técnico (HUD trail + parry por tipeo)

Fecha: 2026-03-16

## Alcance del rollback
Se revierte **solo** lo pedido para sistema de combate:

1. HUD con barra HP trail y efectos visuales asociados.
2. Maniobra de parry/contraataque por tipeo en combate.

> Nota: el minijuego aislado `game/09_TYPING_LAB.rpy` **no se toca** y se conserva para análisis/tuning fuera de combate.

---

## Qué se había implementado

### A) HUD trail de HP (combat HUD)
Se había agregado una capa de barra lagging + lógica de tick para interpolar la vida:
- estado visual por unidad,
- parámetros de hold/rates/aceleración,
- timer recurrente,
- helpers de sync entre HP lógico y visual,
- variante de presets y utilidades de tuning/smoke.

También se añadieron cambios de soporte en flujos de resolución para forzar sincronización visual de barras.

### B) Parry / contraataque por tipeo (combat)
Se había agregado una ruta de resolución de tipeo para contra/parry:
- estado y funciones `bs_counterattack_typing_*`,
- pantalla QTE de combate,
- opción de maniobra `parry_typing`/ramas relacionadas,
- estado persistente y toggles asociados.

---

## Qué hacían esas implementaciones

### HUD trail
Objetivo: mejorar legibilidad del daño con una barra "delayed" (trail) que sigue a la barra frontal con easing.

### Parry por tipeo
Objetivo: resolver parte de la defensa/contraataque mediante habilidad de tipeo en tiempo real, en lugar de depender solo del sistema por dados.

---

## Peso/costo observado (operativo)

En pruebas de juego se observó que la UX no cumplió lo esperado de fluidez/consistencia. A nivel técnico, lo que más pesa en sensación:

- Más trabajo por frame/redraw en HUD de combate (cálculo visual y refrescos frecuentes).
- Timers recurrentes para animación/actualización.
- Mayor complejidad de flujo en defensas (más ramas y estados al resolver).
- Diagnóstico con monitor mostrando fluctuación notable de frame time en escenas de combate con UI activa.

No se detectó un único "bug fatal", sino **costo acumulado + complejidad de integración** para el estado actual del proyecto.

---

## Motivo del rollback (decisión actual)

Se elimina temporalmente porque:

1. No alcanzó el resultado visual/UX esperado en combate.
2. Introdujo complejidad adicional para testeo y depuración del loop defensivo.
3. Se prioriza volver a una base simple y estable (HUD clásico + counterattack por dados).

---

## Estado objetivo después del rollback

- HUD de HP sencillo (sin trail/efectos de lag avanzados).
- Contraataque/parry en combate: **solo por dados**.
- Minijuego de tipeo aislado se mantiene para investigación futura.

---

## Próxima sesión sugerida

Para retomar en otra sesión, conviene reintroducir por etapas:

1. Trail HUD mínimo en entorno de benchmark aislado.
2. Métricas de frame-time con presupuesto fijo por pantalla.
3. Integración por feature flag (on/off) antes de activar por defecto.
4. Parry por tipeo solo después de estabilizar HUD y flujo defensivo.


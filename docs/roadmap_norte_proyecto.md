# Roadmap — Norte del proyecto (Battlestars Saga)

## Visión
Construir un sistema coherente donde:
1. la **cuenta** tenga economía/progreso global,
2. cada **héroe** tenga progreso táctico propio,
3. las recompensas se enruten por modo al destino correcto,
4. toda economía relevante quede auditada para balance.

---

## Arquitectura de progreso (núcleo)

## A) Cuenta (global)
- nivel de cuenta
- EXP de cuenta
- oro global
- baúl general (consumibles/equipables/materiales)
- desbloqueos de modos/features

## B) Héroe (individual)
- identidad (id/nombre/clase/tier)
- técnicas por tier
- stats/build (principalmente Torre)
- inventario de héroe (equipables/consumibles)
- progreso de héroe (exp/nivel si aplica)

### Regla inviolable
- El oro **no** vive en héroes.
- El oro vive en cuenta (baúl/economía global).

---

## Reglas por modo (norte de diseño)

### Duelo libre
- Recompensa principal: oro de cuenta
- EXP de cuenta opcional
- Progreso de héroe: mínimo/no obligatorio

### Torneo C/B/A
- Recompensas: oro + EXP de cuenta
- Progreso de héroe: opcional por reglamento del evento
- Posible economía por rondas/fases

### Torre del cielo
- Recompensas: cuenta + drops
- Progreso de héroe activo (stats/build/exp/nivel)
- Modo de mayor profundidad y dificultad

---

## Líneas de trabajo principales

## 1) Creador de héroes universal
- crear/editar identidad, clase, tier
- asignar técnicas desbloqueadas por tier
- definir uso: NPC Torre / héroe jugable de rotación
- configurar pool/puntos base por contexto
- preview de combate

## 2) Inventario y economía
- baúl de cuenta como hub central
- transferencias baúl -> héroe
- consumos/equipables por héroe
- tienda con respawn
- trazabilidad/auditoría económica

---

## Plan de ejecución recomendado

### Etapa 1 (ya iniciada): Fundaciones
- canon de tipos
- schemas mínimos cuenta/héroe

### Etapa 2 (ya iniciada): Economía e inventarios
- altas de baúl
- transferencias baúl->héroe

### Etapa 3 (ya iniciada): Recompensas por modo
- router de recompensas por `duel_free / tournament / tower`

### Etapa 4 (ya iniciada): Trazabilidad
- log de auditoría de ingresos, transferencias y consumos

### Etapa 5 (siguiente): Integración viva por modo
- conectar recompensas al cierre de combate real (arrancar por Duelo libre)
- luego Torneo C
- luego Torre

### Etapa 6 (siguiente): UI operativa
- pantallas de baúl e inventario de héroe
- acciones de transferencia/consumo desde UI

### Etapa 7 (siguiente): Balance y escalado
- tuning de economía/progresión
- soporte progresivo a 2v2 y variantes competitivas

---

## Criterios de gobernanza (para no perder claridad)
Cada cambio debe declarar:
1. ¿Impacta cuenta, héroe o ambos?
2. ¿Qué modo lo utiliza?
3. ¿Qué evento de auditoría deja?

Si falta alguna de las 3 respuestas, el cambio no está listo para merge.

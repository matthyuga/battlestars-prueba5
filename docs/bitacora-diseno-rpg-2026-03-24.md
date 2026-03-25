#editado el 24 de marzo de 2026
# Bitácora de Diseño — Progresión, Combate, Economía y Loot (2026-03-24)

## Estado
Documento de referencia para retomar el contexto en sesiones futuras.

## Objetivo general
Diseñar un sistema RPG profundo para Battlestars con:
- Progresión por niveles hasta 500.
- 8 atributos base con identidad.
- Escalado de combate por técnicas y desbloqueos.
- Economía de EXP/Oro con anti-abuso.
- Sistema de ítems modular (rareza, sockets, gemas, orbes, sets).

---

## 1) Atributos y filosofía de build

### Atributos definidos
- Fuerza
- Agilidad
- Resistencia
- Inteligencia
- Carisma
- Percepción
- Suerte
- Espíritu

### Criterios acordados
- Carisma y Percepción se enfocan inicialmente en conversación/mapa/misiones (no combate directo por ahora).
- El sistema debe evitar que un atributo haga demasiadas cosas fuertes a la vez.
- Se separan capas conceptuales:
  1. Atributos (identidad y escalado)
  2. Stats de combate (ataque, defensa, hp, recubrimiento, reiatsu, energía)
  3. Utilidad fuera de combate (social, exploración, economía)

### Decisión de progresión de atributos
- 1 punto de stat cada 10 niveles (1 registro).
- Nivel máximo 500 ⇒ 50 puntos base totales.
- Tope por atributo: 20 (base).
- Ruptura excepcional: 25 (mediante contenido especial).

---

## 2) Progresión de combate (kit por niveles)

### Kit inicial (nivel 1)
- Ataque fuerte
- Ataque directo
- Defensa fuerte
- 1 efecto especial a elegir entre 3
- Concentrar x2 fijo (no consume puntos técnicos)

### Desbloqueos por hitos
- Nivel 10: ataque extra + técnica extra + defensa extra
- Nivel 20: ataque reductor + defensa reductora
- Nivel 30: ataque negador + defensa reflectora

### Slice de implementación prioritaria
Primera pieza jugable: "Nueva partida nivel 1" con flujo completo:
1. Selección de especial
2. Asignación de puntos técnicos
3. Guardado
4. Combate sandbox de prueba

---

## 3) Puntos técnicos iniciales

### Decisión cerrada
- Pool inicial técnico: 200 puntos.

### Lineamientos de UX/balance
- Permitir dejar puntos sin gastar (reserva).
- Mostrar siempre: gastado / disponible / tope por técnica.
- Validar en UI que no se superen topes.

---

## 4) Respec (re-edición de build)

### Definición
Respec = redistribuir puntos de stats y/o técnicas.

### Decisión acordada
- Al inicio, tras quest de entrenamiento, otorgar ítem de respec para mejorar onboarding.
- El jugador puede elegir reset de stats, técnicas o ambos (según diseño final de ítems).
- Después del primer uso, respec mediante economía (oro/materiales/quest/cooldown).

### Restricciones recomendadas
- No usar en combate.
- Confirmación doble antes de aplicar.
- Cooldown sugerido: 24h (ajustable).

---

## 5) Niveles y registros

### Estructura
- Nivel máximo: 500.
- 1 registro = 10 niveles.

### Tramos narrativos (idea de contenido)
- 1–100: campaña base
- 100–300: late game (sagas adicionales y personalización profunda)
- 300–400: guerra de alto nivel
- 400–500: contenido extremo/endgame

---

## 6) Economía de EXP y Oro

### Base adoptada
Se toma inspiración de tabla por diferencia de registros (foro), adaptada a videojuego.

### Principios acordados
- Premiar riesgo (underdog) sin romper economía.
- Desincentivar farm de rivales débiles.
- Aplicar anti-abuso por ventanas temporales (24h / 12h / 6h según sistema).

### Anti-abuso
- Cap en recompensas de oro.
- Penalización por repetición de rival/encuentro.
- Ajustes por ventanas horarias y bonos/eventos.

### Documento derivado
- Ver especificación operativa: `docs/PLANILLA_EXP_ORO_DESEMPENO_V1.md`.

---

## 7) Ítems y arquitectura de loot

### Ejes principales
1. Rareza del ítem
2. Nivel de uso
3. Atributos principales/secundarios
4. Sockets
5. Gemas
6. Orbes
7. Sets

### Rareza propuesta
- Común
- Raro
- Especial
- Épico
- Legendario
- Mítico
- Infernal
- Secret (oculto)

### Nivel de uso propuesto
- D (0–20)
- C (20–40)
- B (40–60)
- A (60–80)
- S (80–100)
- SS (100–250)
- SSS (250–400)
- IV (400–500, capa excepcional/oculta)

### Sockets por rareza (base conceptual)
- Común: 0
- Raro: 1
- Especial: 2
- Épico: 3
- Legendario: 4
- Mítico: 5
- Infernal: 6
- Secret: 7

### Notas de diseño
- Puede haber variación de calidad/rareza de socket.
- Crafteo puede abrir socket extra con calidad condicionada por nivel del crafteo/crafter.
- Sets con bonos 2/5, 3/5, 5/5.

---

## 8) Gemas y orbes (lore + sistema)

### Modelo conceptual
- Orbe = núcleo estadístico (partícula mínima con atributos).
- Gema = contenedor/catalizador.
- Socket = interfaz de inserción.
- Ítem = plataforma final de build.

### Resultado
La combinación de orbe+gema+socket+ítem crea variabilidad alta y personalización profunda.

---

## 9) Sistema oculto: Secret + IV

### Decisión de producto/lore
- El sistema público visible se percibe con techo normal hasta infernal.
- Secret/IV NO se comunica como escalón común.
- Se reserva como capa mítica de endgame ultra tardío.

### Intención
- Convertirlo en leyenda/comunidad, no en tier trivial farmeable.
- Posibles puertas narrativas: bóveda encriptada, NPC errante, evento masivo, condiciones especiales.

### Prioridad
- No implementar en fases tempranas.
- Diseñar aparte en etapa final.

---

## 10) Roadmap inicial (alto nivel)


### Documentos de implementación de panel (Ren'Py)
- Contrato v1: `docs/CONTRATO_PANEL_ASIGNACION_RENPY_V1.md`.
- Plan por fases: `docs/PLAN_FASES_IMPLEMENTACION_PANEL_RENPY_V1.md`.
- Ejecución Fase 1: `docs/FASE1_PANEL_RENPY_CORE_EJECUCION_2026-03-25.md`.
- Ejecución Fase 2: `docs/FASE2_PANEL_RENPY_UI_MINIMA_EJECUCION_2026-03-25.md`.

### Fase 1 — MVP jugable
- Sistema nivel/registro + tabla EXP/Oro + anti-abuso básico
- Nueva partida nivel 1
- Selección de especial
- Asignación técnica (pool 200)
- Combate sandbox
- Respec inicial por quest

### Fase 2 — Progresión temprana
- Desbloqueos 10/20/30
- Ajustes de balance de técnicas
- Misiones de build y economía base

### Fase 3 — Loot base
- Ítems con rareza/nivel de uso
- Atributos principales/secundarios
- Equipar/des-equipar

### Fase 4 — Profundidad modular
- Sockets, gemas, orbes
- Crafteo y materiales
- Sets

### Fase 5 — Endgame
- Mítico/Infernal como metagame
- Definición final de Secret/IV (evento legendario)

---

## 11) Preguntas abiertas (para siguientes sesiones)
1. Topes exactos por técnica en niveles altos.
2. Fórmula final de EXP/Oro con multiplicadores por modo (PvE/PvP/evento).
3. Fuentes y sinks de oro para evitar inflación.
4. Tabla de drop de materiales por registros.
5. Reglas exactas de calidad de socket y eficiencia.
6. Detalle final de sets por tipo de equipo.
7. Condiciones narrativas y técnicas de aparición de Secret/IV.

---

## 12) Decisión operativa
Próximo paso: convertir este documento en especificaciones de Sprint 1/Sprint 2 implementables.

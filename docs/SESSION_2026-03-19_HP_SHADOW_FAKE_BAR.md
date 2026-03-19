# Sesión 2026-03-19 — HP Shadow / Fake HP en HUD

## Objetivo de la sesión
Dejar funcional y visible un efecto de **HP falso (gris)** detrás del HP real (celeste) para mejorar lectura del daño, con desaparición controlada para pruebas.

## Resultado final alcanzado
- El segmento gris se muestra correctamente detrás del HP real cuando hay daño.
- El segmento gris mantiene una ventana de permanencia y luego desaparece.
- Se aplicó un desvanecimiento suave al final sin alterar el tiempo objetivo de permanencia.

## Configuración activa al cierre
Archivo: `game/06A_BATTLE_HUD_SYSTEMV2.rpy`

- `HP_FAKE_FX_ALPHA = 1.0`
- `HP_FAKE_FX_DELAY = 1.5`  
  Tiempo total de permanencia del segmento fake tras daño.
- `HP_FAKE_FX_FADE_SECONDS = 0.25`  
  Tramo final del delay donde alpha cae gradualmente hasta 0.
- `HP_FAKE_PLAYER_PERSISTENT = False`  
  No queda congelado permanentemente; desaparece al terminar el ciclo.

## Decisiones técnicas importantes
1. **Capa dual de barra HP**
   - Barra fake gris por debajo.
   - Barra real por encima.

2. **Transparencia de la parte vacía de la barra real**
   - Se dejó transparente para no tapar la capa gris subyacente.

3. **Detección confiable de daño (delta old/new)**
   - Se añadieron trackers dedicados (`hp_fake_last_player_hp`, `hp_fake_last_enemy_hp`) para evitar falsos "sin cambio" cuando otros flujos sincronizan HP antes del render HUD.

4. **Guard para updates sin cambio de HP**
   - Si `new_ratio == old_ratio`, no se resetea/cancela el efecto en cada refresh del HUD.

5. **Fade de cola (tail fade)**
   - El efecto conserva timing global (1.5 s) y aplica fade en el tramo final (0.25 s) para salida más natural.

## Comportamiento esperado en runtime
1. Entra daño.
2. HP real cae (celeste).
3. El tramo descubierto se ve en gris.
4. Permanece hasta completar 1.5 s.
5. En los últimos 0.25 s baja alpha gradualmente.
6. Desaparece.

## Checklist rápido para próxima sesión
- [ ] Probar múltiples golpes consecutivos en menos de 1.5 s.
- [ ] Verificar comportamiento con curación inmediata tras daño.
- [ ] Validar en 1v1 y 2v2 (HUD de unidades y fallback).
- [ ] Ajustar contraste del gris si en ciertos fondos se pierde legibilidad.
- [ ] Decidir si el HP fake pasará a mecánica jugable (stamina/escudo temporal) o se mantiene solo visual.

## Próximos pasos sugeridos
1. Exponer `HP_FAKE_FX_DELAY` y `HP_FAKE_FX_FADE_SECONDS` en un mini panel debug para tuning sin tocar código.
2. Registrar en `battle_log` eventos de creación/consumo de fake HP si se migra a recurso jugable.
3. Si evoluciona a "stamina temporal", definir reglas de prioridad de absorción contra daño real y condición de KO.

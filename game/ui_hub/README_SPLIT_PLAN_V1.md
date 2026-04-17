# UI Hub split plan (v1)

Este directorio prepara la división progresiva de `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`.

## Objetivo
Separar estado, servicios y pantallas para mejorar mantenimiento y reducir riesgo en cambios UI/lógica.

## Estructura objetivo
- `ui_hub_state.rpy`: `default` de estado global, flags de UI y contexto de preparación.
- `ui_hub_roster_service.rpy`: ownership, rotación, resolver roster, helpers de héroes.
- `ui_hub_tech_service.rpy`: perfiles técnicos, pool, allowed-tech por tier y display names.
- `ui_hub_screens_prep.rpy`: `screen bs_saga_preparation_room_screen` y subcomponentes UI de preparación.
- `ui_hub_screens_lobby.rpy`: lobby principal, paneles y navegación superior/inferior.
- `ui_hub_audit_economy.rpy`: compras, oro, inventario de cuenta y auditoría de transacciones.

## Estrategia de migración recomendada
1. **Fase 1 (sin riesgo funcional):** mover definiciones `default` a `ui_hub_state.rpy`. ✅
2. **Fase 2:** migrar helpers puros (sin UI) a `roster_service` y `tech_service`. ✅
3. **Fase 3:** mover pantallas (`screen`) a archivos de UI por dominio.
4. **Fase 4:** mover compra/auditoría/economía a `audit_economy`.
5. **Fase 5:** dejar `12_BATTLESTARS_SAGA_UI_HUB_V1.rpy` como bootstrap/compatibilidad.

## Nota operativa
Hasta completar la migración por fases, el monolito actual sigue siendo la fuente de verdad para evitar regresiones.

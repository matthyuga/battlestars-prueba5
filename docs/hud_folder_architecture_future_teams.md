# Estructura de carpetas HUD (actual + crecimiento a aliados/equipos)

## Respuesta corta

Sí: el agente puede crear carpetas/subcarpetas y dejarlas en commit.
No hace falta que lo hagas desde tu PC.

En este commit se crea la base mínima:
- `game/gui/battle/hud_ai/frames/`
- `game/gui/battle/hud_ai/portraits/`
- `game/gui/battle/hud_ai/icons/`
- `game/gui/battle/hud_ai/thumbnails/`

## ¿Qué pasa con HUD del jugador?

Para no mezclar responsabilidades, conviene separar por **dominio visual**:

```text
game/gui/battle/
  hud_shared/            # piezas compartidas (barras, tipografías, bg comunes)
  hud_player/            # UI del jugador humano
  hud_ai/                # UI de unidades autónomas (enemigas o aliadas NPC)
  hud_neutral/           # opcional: observadores/terceros sin control directo
```

Regla útil:
- `hud_player` = controles interactivos de usuario.
- `hud_ai` = paneles para unidades que actúan solas (enemigo o aliado NPC).

## ¿Aliado NPC cuenta como IA?

Sí.
Si una unidad se mueve sola y no la controlas como jugador, su HUD pertenece a `hud_ai`.

Lo que cambia **no es la carpeta visual**, sino su metadata de combate:
- `team_id` (equipo al que pertenece)
- `faction_id` (facción narrativa, opcional)
- `controller` (`human`, `ai`, `scripted`)
- `relation_to_player` (`ally`, `enemy`, `neutral`) para color/acento visual

## Escalado a 2v2v2 (o más equipos)

No conviene crear carpetas por modo (`2v2`, `3v3`, etc.).
Conviene mantener assets por **rol visual reutilizable** y resolver modo vía datos.

### Estructura recomendada de crecimiento

```text
game/gui/battle/
  hud_shared/
    frames/
    icons/
    themes/

  hud_player/
    frames/
    icons/
    layouts/

  hud_ai/
    frames/              # frame_<style>_<mode>.png
    portraits/           # portrait_<char>_head/full.png
    icons/               # style picker + panel swap + extras
    thumbnails/
    layouts/             # offsets por estilo si hiciera falta

  hud_team/
    accents/             # colores/banderines por team_id
    badges/              # iconitos por equipo/facción
```

## Convención de naming sugerida (future-proof)

- Frames IA: `frame_<style>_<mode>.png`
  - ejemplo: `frame_fantasy_option.png`
- Portraits: `portrait_<char_id>_<variant>.png`
  - variantes: `head`, `full`
- Team accents (cuando llegue 2v2v2):
  - `team_<team_id>_badge.png`
  - `team_<team_id>_accent.png`

## Política práctica para implementar sin deuda

1. Mantener `hud_ai` como carpeta de comportamiento autónomo.
2. No duplicar assets por modo de batalla; sólo por rol/tema.
3. Resolver diferencias de 1v1/2v2/2v2v2 en layout/data, no en filesystem.
4. Dejar fallback visual en `hud_shared` para cuando falte un asset.

## Siguiente paso recomendado

Con esta estructura, la Fase 1 puede arrancar conectando:
1. `frame_<style>_<mode>` por unidad autónoma.
2. `icon_style_picker_arrow_gold` para ciclo de estilo.
3. `icon_panel_swap_blue` para `stat`/`option`.
4. `portrait_<char_id>_head` con fallback.

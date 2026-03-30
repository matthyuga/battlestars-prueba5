# Bitácora de conversación: Koikatsu, Chara Studio e IA

Fecha: 2026-03-29

## Contexto general
- Se revisó de forma exploratoria el perfil público de GitHub de **ManlyMarco**, identificado como desarrollador conocido dentro del ecosistema de modding de Koikatsu/Illusion.
- Se aclaró que los repos públicos suelen contener herramientas, parches y plugins del ecosistema (HF Patch, plugins, utilidades), pero no necesariamente el código fuente oficial completo del núcleo propietario del juego.

## Dudas clave planteadas
1. **Estado de avance de la comunidad de Koikatsu con IA**
   - La conclusión fue que el avance más visible está en workflows alrededor del juego (automatización, catalogación, postproceso, asistencia), más que en una integración IA total y nativa dentro del motor.

2. **¿Puede la IA “entender el programa por dentro”?**
   - Sí, en buena medida, especialmente en capas accesibles por plugins/herramientas/modding e inspección de estructuras.
   - No equivale automáticamente a poseer todo el código fuente interno oficial.

3. **Si el usuario sube su contenido a GitHub, ¿puede analizarse?**
   - Sí: repos, archivos de configuración, contenido técnico, estructura de mods/plugins y metadatos.
   - Se advirtió que archivos binarios o formatos serializados pueden requerir parsing específico.

4. **Lectura de `.zipmod`, plugins, cartas y escenas**
   - Se indicó que se puede analizar gran parte de los datos estructurales/metadatos de esos elementos.
   - Limitaciones dependen de serialización, compresión, versiones y dependencias de plugins.

5. **Animación en Chara Studio (Timeline, FK/IK, expresiones)**
   - Se confirmó que es viable intentar replicación asistida basada en una escena de referencia.
   - Método recomendado: comparar escena origen vs destino, mapear controladores/huesos/tracks, ajustar offsets e iterar.

## Objetivo práctico del usuario (actual)
- Foco en **editor de personajes** y **Chara Studio** para escenas.
- Interés en reducir la dificultad técnica de:
  - búsqueda de objetos,
  - identificación por nombre/ID (incluyendo casos en japonés),
  - combinaciones de shaders/materiales,
  - iluminación y ajustes complejos.

## Propuesta de trabajo sugerida para futuras sesiones
- Empezar con conjuntos pequeños y controlados en lugar de subir todo el juego:
  1. una carta,
  2. una escena,
  3. log de errores (si existe),
  4. lista de plugins/mods.
- Con eso, construir un flujo iterativo de análisis y replicación.

## Nota de continuidad
Este documento sirve como memoria base para retomar el tema en otra sesión sin perder contexto.

---

## Análisis técnico de los archivos subidos en esta rama

Fecha: 2026-03-30

### Archivos detectados
- Carta: `cards/KK_149908.png` (PNG con payload de tarjeta Koikatsu embebido después de `IEND`).
- Escena: `scenes/125904715_p1.png` (PNG con payload de escena embebido después de `IEND`).
- Captura: `cap/CharaStudio-2026-03-26-12-17-23-Render.png` (PNG normal, sin payload extra).
- Mods: `mods/[nHaruka] KKUTS v2.3.zipmod`, `mods/KKUTS.zipmod`.
- Plugins (`.dll`): 16 archivos en `plugins/`.

### Hallazgos sobre la carta de Ichigo
- Se detecta cabecera textual `KoiKatuChara` en el payload.
- Se detecta el nombre `Ichigo` dentro de los datos serializados.
- Se detectan referencias de GUID/IDs de contenido modded (útiles para ubicar zipmods), incluyendo:
  - `com.Blanketman.AdditionalSkinMod`
  - `com.zf9UK2ZA0.Lowrise_pants03`
  - `com.DeathWeasel.Panties`
  - `com.DeathWeasel.AccessoryHairBack`
  - `com.DeathWeasel.AccessoryHairFront`
  - `com.lucentz.nscardigan`
- También aparecen referencias a plugins de edición/material:
  - `com.deathweasel.bepinex.materialeditor`
  - `com.deathweasel.bepinex.clothingunlocker`
  - `com.deathweasel.bepinex.hairaccessorycustomizer`
  - `com.deathweasel.bepinex.pushup`
  - `com.deathweasel.bepinex.uncensorselector`

### Hallazgos sobre la escena
- Se detecta payload embebido muy grande tras `IEND`, consistente con datos de escena de Chara Studio.
- Se observan referencias repetidas a shaders/materiales del tipo:
  - `Shader Forge/main_opaque`
  - `Shader Forge/main_skin`
  - `Shader Forge/main_item`
  - `Shader Forge/main_hair`
  - `Shader Forge/main_hair_front`
  - `Shader Forge/toon_eye_lod0`
  - `Shader Forge/toon_eyew_lod0`
- Esto confirma que sí se pueden extraer pistas de configuración visual para replicar look & feel.

### Hallazgos sobre zipmods KKUTS
- Ambos zipmods incluyen `manifest.xml` con:
  - `guid`: `KKUTS`
  - `name`: `KKUTS`
  - `version`: `2.3` (en `[nHaruka] KKUTS v2.3.zipmod`)
  - `author`: `nHaruka`
  - `game`: `Koikatsu`
- Incluyen bundles de shader/material para chara/item/hair y variantes tessellation (`kkuts*.unity3d`).

### Hallazgos sobre plugins
- Los 16 archivos en `plugins/` son DLLs .NET/Unity válidas (cabecera `MZ`).
- Se detectan, entre otros:
  - `AccMover.Koikatu.dll`
  - `AnimeAssAssistant.Koikatu.dll`
  - `AnimationLoader.Koikatu.dll`
  - `BetterSceneLoader.Koikatu.dll`
  - `BetterScaling.Koikatu.dll`
  - `AxisUnlocker.Koikatu.dll`
  - utilidades `BepInEx.*` (MessageCenter, InputHotkeyBlock, MuteInBackground, etc.)

### Qué puede hacer Codex con este material (de forma práctica)
1. Inventario automático de dependencias (GUIDs de zipmods/plugins) por carta/escena.
2. Checklist de faltantes para que una carta/escena cargue sin errores.
3. Extracción de referencias de shader/material para recrear estilos visuales.
4. Base de búsqueda de objetos por nombre técnico/GUID detectado.
5. Comparación entre dos cartas o dos escenas para ver cambios de configuración.

### Límites actuales (sin más tooling)
- No se reconstruye al 100% la escena animada solo con strings; para eso conviene parser dedicado de formato de escena + lectura de datos serializados completos.
- No se garantiza mapear cada objeto/hueso/keyframe sin exportadores o herramientas adicionales del ecosistema KK/Studio.

### Próximo paso recomendado
- Subir una segunda versión de la misma escena (v1/v2) y una segunda carta (v1/v2). Con eso se puede generar diff técnico (qué cambió en materiales, luces y parámetros) y convertirlo en receta reproducible.

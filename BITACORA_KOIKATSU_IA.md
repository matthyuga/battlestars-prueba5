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

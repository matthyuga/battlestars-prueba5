# Roadmap — Economy Toolkit Complete & Executable (v1)

Fecha: 2026-04-12
Estado: Propuesto + parcialmente implementado (release packaging base)

## Visión final

Tener un toolkit **completo y funcional** que se pueda usar en 3 niveles:

1. **Dev/QA técnico**: Python CLI y Makefile.
2. **Equipo no técnico**: binario ejecutable (`economy-toolkit` / `.exe`).
3. **Entrega de producto**: releases versionadas con artefactos por plataforma.

---

## Estado actual

### Fase A — Core Economy Lab (completada)
- Simulador (`economy_lab.py`)
- Freeze baseline (`run_economy_baseline.py`)
- Compare + gate (`compare_economy_baselines.py`)
- Dashboard HTML (`economy_dashboard.py`)

### Fase B — Operación integrada (completada)
- Toolkit unificado (`economy_toolkit.py`): `simulate`, `freeze`, `compare`, `dashboard`, `cycle`.
- CI funcional de validación (`.github/workflows/economy-tools.yml`).

### Fase C — Release packaging (iniciada en este paso)
- Builder ejecutable one-file (`build_economy_toolkit_executable.py`).
- Packager release ZIP + SHA256 (`package_economy_toolkit_release.py`).
- Workflow multi-OS de release (`.github/workflows/economy-release.yml`).

---

## Próximas fases sugeridas

### Fase D — Hardening de distribución
1. Firma de binarios/código por plataforma.
2. Convención de versionado semántico (`economy-toolkit-vMAJOR.MINOR.PATCH`).
3. Changelog de release automático.
4. Verificación de checksum en pasos de consumo interno.

### Fase E — UX de producto ejecutable
1. Comando `wizard` interactivo (menú guiado) para perfiles no técnicos.
2. Plantillas de ejecución (`profiles/`) cargables por nombre.
3. Empaquetado de salida con report bundle (diff + dashboard + manifest).

### Fase F — Calidad y soporte
1. Tests unitarios para fórmulas y comparador.
2. Tests de regresión de escenarios fijos (golden files).
3. Pruebas cross-platform del binario en CI.
4. Manual de operación para QA/Design/PM.

---

## Criterio de “toolkit completo”

Se considera completo cuando:
- Build ejecutable y release multi-OS son 100% automáticos,
- hay verificación de calidad (tests + gate) previa al release,
- y una persona no técnica puede correr el flujo principal sin tocar Python/Makefile.

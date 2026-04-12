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

### Fase D — Hardening de distribución (en progreso)
1. [x] Convención de versionado semántico (`economy-toolkit-vMAJOR.MINOR.PATCH`) validada en CI.
2. [x] Changelog de release automático en workflow de publicación.
3. [x] Verificación de checksum en pasos de consumo interno (script + target Make).
4. [~] Firma por plataforma:
   - [x] Attestation de provenance en CI.
   - [ ] Firma criptográfica de binarios por plataforma (pendiente integrar certificado/secretos por SO).

### Fase E — UX de producto ejecutable (implementada base)
1. [x] Comando `wizard` interactivo (menú guiado) para perfiles no técnicos.
2. [x] Plantillas de ejecución (`tools/profiles/`) cargables por nombre.
3. [x] Empaquetado de salida con report bundle (diff + dashboard + manifest).
4. [ ] UX avanzada: wizard con validación contextual y presets por rol (QA/Design/PM).

### Fase F — Calidad y soporte (implementada base)
1. [x] Tests unitarios para fórmulas y comparador.
2. [x] Tests de regresión de escenarios fijos (golden files).
3. [x] Pruebas cross-platform del binario en CI (smoke `--help` post-packaging).
4. [x] Manual de operación para QA/Design/PM.
5. [ ] Siguiente mejora: ampliar cobertura de tests de stress/performance.

---

## Criterio de “toolkit completo”

Se considera completo cuando:
- Build ejecutable y release multi-OS son 100% automáticos,
- hay verificación de calidad (tests + gate) previa al release,
- y una persona no técnica puede correr el flujo principal sin tocar Python/Makefile.


## Estado de criterio de “toolkit completo"

- [x] Build ejecutable y release multi-OS automáticos.
- [x] Verificación de calidad (tests + gate) previa a release.
- [x] Flujo principal no técnico disponible vía ejecutable + wizard.
- [~] Hardening avanzado de firma nativa por SO (pendiente certificados por plataforma).

# Configuración y Directivas del Agente de Programación

## Entorno y Modelo
- **Harness:** Visual Studio Code (GitHub Copilot Edits / Modo Agente)
- **Modelo:** Auto (selección adaptativa de modelo en VS Code)
- **Motivo de elección:** Integración directa con el editor, ejecución local controlada y trazabilidad de cambios en archivos locales sin servicios de pago adicionales.

## Herramientas y Permisos
- **Lectura y escritura:** Acceso a directorios del proyecto (`data/`, `src/`, `tests/`).
- **Terminal:** Ejecución de pruebas unitarias (`pytest`) y scripts locales.
- **Control humano obligatorio:** Toda modificación de código y ejecución de scripts debe ser revisada y aceptada manualmente tras inspección de diffs.

## Reglas de Dominio y Negocio
1. **Inventario:** 5 unidades predefinidas (MIC-01, MIC-02, OSC-01, MUL-01, FUE-01). No se administra ni modifica el inventario.
2. **Intervalo:** Modelo de intervalo semiabierto `[inicio, fin)`.
3. **Solapamiento:** Existe conflicto si y solo si:
   `nuevo_inicio < fin_existente` y `nuevo_fin > inicio_existente` sobre la misma unidad en estado `ACTIVA`.
4. **Adyacencia:** Se permiten límites consecutivos exactos (`10:00-11:00` y `11:00-12:00`).
5. **Simultaneidad:** Unidades distintas pueden reservarse en franjas idénticas simultáneamente.
6. **Cancelación:** Cambia a estado `CANCELADA`, conserva identificador y metadatos en historial, y libera el intervalo.
7. **Persistencia:** Almacenamiento local atómico en archivo JSON (`data/reservas.json`).
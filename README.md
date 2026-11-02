 # Laboratorio de Ensayos - Sistema Automatizado de Gestión de Turnos

## Sección 1: Especificación

### Contexto del Problema
La administración de los equipos de laboratorio se coordinaba históricamente mediante planillas compartidas y mensajería directa. Esta dinámica generó bloqueos indebidos de instrumentos debido a turnos dados de baja que nunca se liberaron formalmente, así como superposiciones operativas entre solicitudes simultáneas para un mismo dispositivo físico.

### Objetivo y Alcance
Desarrollo de un sistema de control local en Python, verificable mediante pruebas automáticas, que garantiza la consulta de disponibilidad en tiempo real, la adjudicación de turnos sin solapamiento y la anulación controlada de reservas preservando el rastro histórico completo. El estado del sistema se almacena en disco de manera persistente en formato JSON local (`data/reservas.json`).

### Parque de Instrumentos (Inventario Base)
El sistema opera sobre un conjunto fijo de 5 dispositivos físicos de laboratorio preconfigurados:

| Identificador | Descripción del Dispositivo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

### Reglas de Negocio y Supuestos Operativos
1. **Entidad de Reserva:** Cada registro almacena un identificador único (UUID v4), el código del equipo (`item_id`), el nombre o legajo del solicitante (cadena no vacía ni formada únicamente por espacios), fecha/hora de inicio, fecha/hora de cierre y el estado de la reserva (`ACTIVA` o `CANCELADA`).
2. **Definición de Intervalo Temporal:** Toda reserva activa se modela matemáticamente como un intervalo semiabierto `[inicio, fin)`.
3. **Condición de Conflicto (Solapamiento):** Dos reservas sobre el mismo dispositivo físico colisionan si y solo si sus rangos se cruzan: `nuevo_inicio < fin_existente` y `nuevo_fin > inicio_existente`.
4. **Adyacencia Consecutiva:** Se admiten turnos contiguos en el mismo equipo sin margen muerto; una reserva que finaliza a las 11:00 permite el inicio de otra exactamente a las 11:00.
5. **Concurrencia entre Equipos:** Dispositivos físicos distintos (por ejemplo, MIC-01 y MIC-02) pueden reservarse en franjas idénticas sin ninguna clase de bloqueo.
6. **Políticas de Fecha y Hora (Supuestos):** Se adopta el formato estándar ISO-8601 (`YYYY-MM-DDTHH:MM`). Para posibilitar la ejecución de pruebas unitarias deterministas y reproducibles en cualquier momento, el sistema no restringe de forma arbitraria fechas pasadas.
7. **Política de Cancelación:** La anulación de una reserva no elimina el registro; cambia su estado a `CANCELADA`, manteniendo sus metadatos e ID para trazabilidad histórica y liberando el rango horario para nuevas solicitudes.

### Criterios de Aceptación Verificables
- **REQ-RES-01:** La creación de una reserva con equipo registrado, solicitante válido e `inicio < fin` produce un registro con estado `ACTIVA` y un identificador único persistido.
- **REQ-RES-02:** El sistema rechaza cualquier solicitud con solicitante en blanco, compuesto solo por espacios o de tipo no admisible.
- **REQ-RES-03:** El sistema rechaza rangos temporales anómalos donde `inicio >= fin` o cadenas con formato de fecha ilegible.
- **REQ-RES-04:** Se deniega cualquier reserva activa que colisione de forma total, parcial o envolvente con otra reserva activa preexistente para la misma unidad.
- **REQ-RES-05:** Se aceptan reservas contiguas donde el inicio coincide con el fin de una reserva activa anterior en la misma unidad.
- **REQ-RES-06:** Se permite registrar reservas simultáneas en la misma ventana horaria siempre que pertenezcan a unidades distintas.
- **REQ-RES-07:** Al cancelar una reserva, se actualiza el estado a `CANCELADA`, se preserva el ID en el registro y el intervalo queda disponible para nuevas consultas.
- **REQ-RES-08:** Toda la información persistida en `data/reservas.json` se recupera intacta tras reiniciar la ejecución de la aplicación.
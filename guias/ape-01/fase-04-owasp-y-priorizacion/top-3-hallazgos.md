# Tres hallazgos prioritarios para presentar

> Esta selección técnica previa incluye la escritura en competencia detenida. Para los tres hallazgos de la entrega basada en el reporte proporcionado, consultar la [selección contextualizada](matriz-priorizacion-para-reporte.md#tres-hallazgos-seleccionados).

Selección de riesgos reproducidos, sin depender de una clave de producción ausente o de demostrar alcance de CVEs.

1. **HAL-006 — Escritura en competencia detenida (A06).** Impacto 3, probabilidad 2, riesgo 6. P07 devolvió 201 y persistió 15 registros en una competencia detenida porque se validó la competencia de otro equipo del juez. Priorizar por integridad del resultado y cierre de competencia. Corregir comprobando el equipo objetivo y su competencia.
2. **HAL-004 — Tiempos negativos (A06).** Impacto 3, probabilidad 2, riesgo 6. P05 guardó 15 tiempos negativos. Requiere juez asignado y competencia válida, pero compromete directamente el dato central del sistema. Validar el lote completo con las reglas de negocio.
3. **HAL-002 — Login sin limitación de intentos (A07).** Impacto 3, probabilidad 2, riesgo 6. P03 observó seis rechazos sin bloqueo y posterior login correcto; el código no configura throttle. Facilita adivinación de credenciales y se combina con HAL-003. Agregar límites por cuenta/IP, MFA y alertas.

**Para la práctica de IDOR:** HAL-001 también ofrece una demostración clara: el estado del equipo ajeno responde 200 aunque el detalle responde 404. Su impacto se valoró de forma moderada porque parte de los tiempos se muestra en vistas públicas.

**Condición de urgencia:** si algún despliegue usa la clave pública de fallback (HAL-008), detener ese despliegue, rotar la clave e invalidar los tokens afectados antes de continuar.

[Detalle y correcciones](hallazgos-server5k.md) · [Matriz](matriz-priorizacion.md) · [Evidencias](evidencias/revision-server5k/README.md)

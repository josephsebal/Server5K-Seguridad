# Informe de fase 3 — errores y fugas de información

Fuente documental: [Reporte de los integrantes](../../../entregas/APE-01-reporte-publicacion.pdf), sección conjunta de fases 3 y 4, páginas físicas 9–12. El PDF no separa un informe de errores por cada sesión: se organiza aquí la parte correspondiente, apoyada en las evidencias técnicas ya existentes.

## Avance documentado

Se revisaron entradas incorrectas en login y registros, mensajes devueltos al cliente, comportamiento de DEBUG y el contexto de los logs. Se observaron respuestas 500 por tipos JSON incorrectos y una respuesta con detalle de AttributeError. Con DEBUG=True se reprodujeron traza y ruta interna; no se comprobó esa exposición en producción.

El reporte propone mensajes genéricos para el usuario y conservar detalles en logs restringidos. La prueba de A09 muestra que el rechazo de login registra fecha y ruta, pero no cuenta intentada ni origen.

## Entregables

- [Registro de casos y resultados](registro-errores.md).
- [Correcciones propuestas](correcciones.md).
- [Hallazgos técnicos](../fase-04-owasp-y-priorizacion/hallazgos-server5k.md), HAL-005, HAL-007 y HAL-010.
- [Log de la demostración web](../fase-04-owasp-y-priorizacion/evidencias/revision-server5k/EVI-A09-log-login-rechazado.txt).

## Estado y límites

Se documentaron más de cinco casos de error, no cinco fugas diferentes confirmadas. No se publican capturas de depuración que puedan contener secretos. No se implementaron las correcciones ni se presentan comprobaciones después de corregir; esa actividad queda pendiente. La subida de archivos no se probó dentro del módulo de jueces revisado.

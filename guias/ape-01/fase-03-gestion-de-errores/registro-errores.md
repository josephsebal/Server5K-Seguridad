# Registro de errores — revisión local Server5K

Pruebas aisladas, datos sintéticos y base temporal. No se provocaron errores en la base real. [JSON completo](../fase-04-owasp-y-priorizacion/evidencias/revision-server5k/resultados-pruebas.json).

| Caso | Entrada / escenario | Resultado | Fuga | Referencia |
| --- | --- | --- | --- | --- |
| Credenciales inválidas | Seis intentos con contraseña sintética errónea | 401 genérico | No se observó fuga en el mensaje | P03 |
| Campos incompletos | Login con objeto vacío | 400, campos requeridos | No se observó fuga técnica | P08 |
| Objeto raíz incorrecto | Login con lista JSON y DEBUG=False | 500 genérico | No hubo traza en el cliente; falta validación | P09 |
| Tipo de registros incorrecto | `registros: 15`, autenticado | 500 genérico | No hubo traza con DEBUG=False | P10 |
| Tipo de ítem incorrecto | Lista de 15 cadenas | 400, `Error general: 'str' object has no attribute 'get'` | Sí, detalle de implementación; baja exposición por sí sola | P11 |
| Refresh incorrecto | `refresh` como lista | 400, validación de cadena | No se observó fuga técnica | P12 |
| Excepción con depuración | Login con lista y DEBUG=True | 500 con traceback y ruta | Sí, fuga condicionada al modo DEBUG expuesto | P13 |
| Recurso inexistente | URL inexistente, DEBUG=False | 404 | No se observó fuga técnica | P14 |
| Lote incompleto | Un tiempo válido y 14 objetos vacíos | 201 y persistencia parcial; reintento 400 | Sin fuga; estado de negocio inconsistente | P06 |

Se ejecutaron más de cinco casos, pero **no se afirman cinco fugas diferentes**. No se evaluó carga de archivos: no se identificó una función de subida para el juez dentro del alcance revisado. Capturas manuales de navegador pendientes si la docente las exige.

Correcciones propuestas y severidad: [HAL-005/HAL-007](../fase-04-owasp-y-priorizacion/hallazgos-server5k.md). No se aplicaron cambios al código.

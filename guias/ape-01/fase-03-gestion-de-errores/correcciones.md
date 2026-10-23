# Correcciones propuestas y seguimiento

Estado: propuestas documentadas, sin cambios aplicados al código funcional. No se presenta evidencia posterior a una corrección que no se ha implementado.

| Caso | Mensaje o comportamiento observado | Resultado recomendado | Componente | Evidencia previa | Estado |
| --- | --- | --- | --- | --- | --- |
| JSON raíz de login tipo lista | Error 500 por uso de .get() | 400: «Envíe un objeto con username y password». | app/views/auth_views.py | P09 y P13 | Propuesto |
| registros con tipo numérico | Error 500 por len() | 400: «registros debe ser una lista de 15 elementos». | app/views/registro_views.py | P10 | Propuesto |
| Ítems de registros tipo cadena | Se devuelve detalle de AttributeError | 400: «Cada registro debe ser un objeto con un tiempo válido». | app/services/registro_service.py | P11 | Propuesto |
| Excepción inesperada | Ramas que interpolan str(e) | Mensaje genérico con referencia; detalle sólo en log restringido. | Vistas y servicio | Revisión de código y HAL-007 | Propuesto |
| Lote parcialmente inválido | Guarda un tiempo y bloquea reintento | Rechazar íntegramente o definir recuperación coherente y auditable. | Servicio de registros | P06 / HAL-005 | Propuesto |

Para excepciones inesperadas de servidor se conserva 500; no corresponde convertirlas todas en 400. Los 400 se reservan para errores de entrada identificados.

[Resultados originales](../fase-04-owasp-y-priorizacion/evidencias/revision-server5k/resultados-pruebas.json)

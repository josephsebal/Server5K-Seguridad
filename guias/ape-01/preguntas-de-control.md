# Respuestas propuestas — Guía APE 01

Estas son las cuatro preguntas de la guía original. Las diez preguntas de las simulaciones OWASP están en [Respuestas OWASP](fase-04-owasp-y-priorizacion/README_Practica_OWASP_Top10_2025.md). Adaptar a la voz y conclusiones de los integrantes.

## 1. Superficie de ataque e inventario

Un inventario permite saber qué entradas y funciones pueden usar visitantes, jueces y administradores, y asignar pruebas y controles a cada una. No basta revisar las páginas: hay rutas API, parámetros, cabeceras, WebSocket y dependencias. Omitir un componente deja una vía sin evaluar. Server5K lo demuestra: el detalle de equipos filtra por juez, pero `/api/equipos/{id}/registros/estado/` recupera por ID sin el mismo control y devuelve datos de otro equipo (HAL-001). Revisar sólo la interfaz o la ruta principal habría pasado por alto esa diferencia.

## 2. Priorización de la tríada CIA con recursos limitados

Se prioriza según el daño al objetivo del sistema, sensibilidad de los datos, exposición y probabilidad; no se asigna automáticamente el mismo nivel a todos los activos. En Server5K la integridad de los tiempos y resultados tiene un peso alto: aceptar tiempos negativos o editar una competencia detenida cambia la clasificación de la carrera (HAL-004/HAL-006). Para ese activo priorizaría validación de negocio y estados de competencia. Para credenciales priorizaría confidencialidad y autenticación; durante la carrera también es esencial la disponibilidad. Los demás pilares siguen requiriendo controles básicos, respaldo y recuperación.

## 3. Depuración frente a mensajes seguros

Separar configuraciones por entorno: DEBUG sólo en laboratorio y desactivado en producción. Validar entradas y centralizar el manejo de errores, dar mensajes claros pero genéricos con código de referencia y registrar el detalle en logs restringidos. Nunca revelar contraseñas, tokens, claves, cadenas de conexión, datos personales, consultas sensibles, rutas o stack traces al usuario final. En Server5K, enviar una lista JSON al login causa una excepción: con DEBUG=True se observaron traceback y rutas; con DEBUG=False el 500 es genérico. Además hay errores que incluyen str(e) incluso fuera del modo DEBUG (HAL-007), por lo que desactivar DEBUG por sí solo no basta.

## 4. OWASP y priorización por impacto/probabilidad

OWASP Top 10 agrupa clases de riesgo; no es una lista de diez pruebas que certifique seguridad. Cada hallazgo requiere evidencia, alcance y condiciones. En Server5K, consultar registros ajenos encaja en A01; la falta de límites y la política de contraseñas en A07; los errores no controlados en A10. La clave pública de fallback tendría impacto crítico si un despliegue la usara, pero la clave local está configurada; las escrituras fuera de competencia sí se reprodujeron. Por ello la prioridad depende tanto del daño como de la posibilidad de ocurrencia, y de si el escenario existe en el entorno evaluado. Un aviso de dependencia exige además comprobar si el camino vulnerable se utiliza.

[Informe de revisión](fase-04-owasp-y-priorizacion/hallazgos-server5k.md) · [Fuente OWASP](https://top10.owasp.org/2025/)

## Respuestas aportadas por los autores

[Transcripción de las preguntas y respuestas del documento completo](preguntas-del-documento.md). Las respuestas anteriores se conservan como propuestas de apoyo; no reemplazan silenciosamente la redacción entregada por los integrantes.

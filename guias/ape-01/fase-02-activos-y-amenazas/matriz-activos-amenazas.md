# Matriz de activos, amenazas y clasificación CIA

Fuente: [Reporte de los integrantes](../../../entregas/APE-01-reporte-publicacion.pdf), páginas físicas 6–9. Se incorporan los **12 activos de la tabla del documento**; se añaden IDs ACT para trazabilidad. La conclusión original menciona diez activos, pero su tabla enumera doce.

C = confidencialidad, I = integridad y D = disponibilidad. Alto: daño importante al objetivo del sistema; medio: información operativa o función recuperable; bajo: información pública o efecto menor, según el pilar evaluado.

| ID | Activo | C | I | D | Amenaza | Controles descritos en el reporte | Prioridad |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ACT-001 | Credenciales de jueces | Alto | Alto | Medio | Robo, fuerza bruta o reutilización | Hash de contraseña y JWT | Alta |
| ACT-002 | Claves JWT y refresh tokens | Alto | Alto | Alto | Robo, falsificación o replay | Firma HS256 y blacklist | Alta |
| ACT-003 | Datos personales de jueces | Alto | Medio | Medio | Enumeración o acceso de otro juez | /api/me/ del usuario autenticado | Alta |
| ACT-004 | Asignación juez-equipo | Medio | Alto | Alto | Manipulación de IDs e IDOR | Filtro por juez y validación en POST | Alta |
| ACT-005 | Datos de competencia | Bajo | Alto | Alto | Alteración de estado o borrado | Django Admin y relaciones del modelo | Alta |
| ACT-006 | Registros de tiempo | Medio | Alto | Alto | Inserción inválida, duplicación o borrado | Transacciones, UUID e idempotencia declarados | Alta |
| ACT-007 | Resultados públicos | Bajo | Alto | Alto | Manipulación o indisponibilidad durante el evento | Vistas de sólo lectura | Media |
| ACT-008 | Mensajes y canales WebSocket | Medio | Alto | Alto | Suplantación, escucha o saturación | JWT y verificación de juez_id | Alta |
| ACT-009 | Base de datos | Alto | Alto | Alto | Exfiltración, corrupción o ransomware | PostgreSQL o SQLite según entorno | Alta |
| ACT-010 | Logs y trazas | Alto | Medio | Medio | Exposición de tokens, rutas o datos sensibles | Logging configurado; querystring WS no registrado explícitamente por el consumer | Alta |
| ACT-011 | Configuración y secretos | Alto | Alto | Alto | Clave por defecto o filtración de .env | Variables de entorno documentadas | Alta |
| ACT-012 | Código y dependencias | Medio | Alto | Medio | Componente vulnerable o CVE | uv.lock y requirements.txt | Media |

## Interpretación y límites

La clasificación expresa la importancia de proteger cada activo, no demuestra que su amenaza haya ocurrido. Se mantiene la valoración de los autores: la integridad de tiempos y resultados es esencial para una competencia, y la confidencialidad de credenciales y secretos requiere protección alta.

Los controles se transcriben como mecanismos descritos, no como garantías de eficacia. Las pruebas mostraron, por ejemplo, que el filtro por juez no se aplica de manera uniforme y que el flujo HTTP acepta tiempos negativos. Disponer de una base de datos, una transacción o un lockfile no acredita por sí solo cifrado, respaldo, validación completa o actualización de componentes.

[Dos controles propuestos por activo](controles-mitigacion.md) · [Relación con hallazgos y matriz de riesgo](../fase-04-owasp-y-priorizacion/matriz-priorizacion-para-reporte.md)

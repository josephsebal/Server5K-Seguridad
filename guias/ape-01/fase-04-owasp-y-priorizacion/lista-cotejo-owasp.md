# Lista de cotejo OWASP Top 10:2025 — Server5K

Fuente de categorías: https://top10.owasp.org/2025/. Consulta: 21/10/2026. Revisión limitada del commit indicado en el informe; no certificación de seguridad.

| Categoría | Nombre oficial | Estado | Evidencia | Conclusión |
| --- | --- | --- | --- | --- |
| A01 | Broken Access Control | HAL-001 confirmado; controles positivos en otras rutas | P01/P02/P18/P19 | El estado de registros no aplica el mismo aislamiento por juez que el detalle. |
| A02 | Security Misconfiguration | Condicionado al despliegue | P13/P14 y settings | DEBUG local reproduce trazas; no se confirmó producción expuesta. |
| A03 | Software Supply Chain Failures | HAL-009; SCA positivo, alcance pendiente | pip-audit.json; lock/requirements/Dockerfile | Se requieren actualización y resolución única; no convertir cada aviso en ataque confirmado. |
| A04 | Cryptographic Failures | HAL-008 condicional; hash positivo | P04/P17 | PBKDF2 con sal correcto; clave pública de fallback peligrosa si se usa. |
| A05 | Injection | No confirmado en pruebas limitadas | P15/P16 | Login SQL de prueba rechazado y salida HTML escapada; ampliar cobertura. |
| A06 | Insecure Design | HAL-004 y HAL-006 confirmados | P05/P07 | Reglas de negocio de tiempos y estado de competencia insuficientes. |
| A07 | Authentication Failures | HAL-002 y HAL-003 confirmados | P03/P04 | Sin limitación local visible y formulario acepta contraseña débil. |
| A08 | Software or Data Integrity Failures | Sin explotación confirmada; observación de construcción | Dockerfile:26; HAL-009 | Herramienta latest sin digest; agrupar con cadena de suministro y evitar duplicar. |
| A09 | Security Logging and Alerting Failures | HAL-010; cobertura incompleta en código | P03; auth_views/settings | Hay logs genéricos, faltan eventos de autenticación con contexto y alertas visibles. |
| A10 | Mishandling of Exceptional Conditions | HAL-005 y HAL-007 confirmados | P06/P09/P10/P11/P13 | Lote parcial bloquea recuperación y tipos incorrectos generan 500/detalles. |

## Comprobaciones específicas de la guía

- Sesiones/tokens: revisado parcialmente; JWT y rechazo WS confirmados. Revocación completa y caducidad WS pendientes.
- CSRF: middleware presente; no probado con navegador/cookies y enforce_csrf_checks. No declarar fallo por usar Authorization Bearer.
- Cabeceras: tres defensas presentes en P14; proxy, TLS y CSP del despliegue pendientes.
- Contraseñas: PBKDF2 con sal confirmado y política de jueces insuficiente.
- Exposición de datos: acceso de juez a equipo ajeno confirmado; DEBUG condicionado al entorno.
- Componentes: SCA ejecutado sobre paquetes instalados; alcance y deduplicación CVE pendientes.

[Informe completo](hallazgos-server5k.md) · [Respuestas y texto para la práctica](README_Practica_OWASP_Top10_2025.md) · [Evidencias](evidencias/revision-server5k/README.md)

## Registro para la actividad

[Rutas, archivos, solicitudes, resultados y texto para pegar por categoría](registro-detallado-por-categoria.md). Las expresiones «control efectivo» se limitan a lo probado; «no aplica» se usa sólo para una funcionalidad no identificada, no por ausencia de hallazgos.

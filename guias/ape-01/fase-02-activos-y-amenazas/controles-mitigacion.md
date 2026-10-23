# Controles propuestos por activo

Fuente: [Reporte de los integrantes](../../../entregas/APE-01-reporte-publicacion.pdf), páginas físicas 7–9. Se separan los dos controles de cada activo para facilitar su seguimiento. Son propuestas: no se afirma su implementación.

| Activo | Control propuesto 1 | Control propuesto 2 | Estado |
| --- | --- | --- | --- |
| ACT-001 — Credenciales de jueces | Limitar intentos fallidos de login | MFA y contraseñas seguras al crear cuentas | Propuesto; implementación pendiente |
| ACT-002 — Claves JWT y refresh tokens | Renovación y revocación de tokens según necesidad | Proteger transmisión con HTTPS y gestión segura de sesión | Propuesto; implementación pendiente |
| ACT-003 — Datos personales de jueces | Mostrar sólo datos personales necesarios | Comprobar propiedad y registrar accesos | Propuesto; implementación pendiente |
| ACT-004 — Asignación juez-equipo | Comprobar permisos de consulta y modificación | Probar aislamiento entre cuentas | Propuesto; implementación pendiente |
| ACT-005 — Datos de competencia | Permisos por rol | Registro de cambios y respaldos recuperables | Propuesto; implementación pendiente |
| ACT-006 — Registros de tiempo | Validar tiempos e historial de cambios | Respaldar y comprobar recuperación | Propuesto; implementación pendiente |
| ACT-007 — Resultados públicos | Caché coherente con la información original | Monitoreo y alertas de errores | Propuesto; implementación pendiente |
| ACT-008 — Mensajes y canales WebSocket | WSS y tokens con validez limitada | Límites de tamaño y cantidad de mensajes | Propuesto; implementación pendiente |
| ACT-009 — Base de datos | Cifrado y mínimo acceso autorizado | Respaldos cifrados y pruebas de restauración | Propuesto; implementación pendiente |
| ACT-010 — Logs y trazas | Excluir contraseñas y tokens de los eventos | Restringir acceso y definir retención | Propuesto; implementación pendiente |
| ACT-011 — Configuración y secretos | Impedir inicio productivo sin clave segura | Guardar claves en un gestor de secretos | Propuesto; implementación pendiente |
| ACT-012 — Código y dependencias | Escaneo automático de dependencias | Actualizar y volver a probar compatibilidad | Propuesto; implementación pendiente |

## Prioridad de aplicación

Primero, proteger tiempos y acceso de los jueces: validación de lotes, permisos por objeto, límite de intentos y política de contraseñas. Después, revisar registros de auditoría, despliegue y dependencias según su exposición real. HTTPS/WSS se deben verificar en el despliegue previsto, sin confundir HTTP de laboratorio con exposición productiva.

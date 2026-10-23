# Inventario de superficie de ataque

Fuente: [Reporte de los integrantes](../../../entregas/APE-01-reporte-publicacion.pdf), páginas físicas 5–6. Se conservan los identificadores SA del reporte.

| ID | Elemento | Ubicación | Actor |
| --- | --- | --- | --- |
| SA-01 | Login personalizado | POST /api/login/ | Cualquier cliente |
| SA-02 | Refresh personalizado declarado | POST /api/token/refresh/ | Cliente con refresh token |
| SA-03 | Refresh estándar en server/urls.py | POST /api/token/refresh/ | Cliente con refresh token |
| SA-04 | Logout y blacklist | POST /api/logout/ | Juez autenticado |
| SA-05 | Perfil propio | GET /api/me/ | Juez autenticado |
| SA-06 | Competencias | GET /api/competencias/; /api/competencias/{id}/ | Juez autenticado |
| SA-07 | Equipos | GET /api/equipos/; /api/equipos/{id}/ | Juez autenticado |
| SA-08 | Registro masivo de tiempos | POST /api/equipos/{id}/registros/ | Juez autenticado |
| SA-09 | Estado de registros | GET /api/equipos/{id}/registros/estado/ | Juez autenticado |
| SA-10 | Estado público de competencias | GET /api/admin/estado-competencias/ | Anónimo |
| SA-11 | Documentación OpenAPI | /api/schema/; /api/docs/; /api/redoc/ | Anónimo, según configuración |
| SA-12 | Vistas públicas | /; /{id}/; /equipo/{id}/ | Anónimo |
| SA-13 | WebSocket de juez | ws://host/ws/juez/{id}/?token=… | Juez con JWT |
| SA-14 | Panel administrativo | /admin/ | Administrador |
| SA-15 | Estáticos y multimedia declarados | /static/; /media/ | Cliente web, según despliegue |
| SA-16 | Health check | GET /api/health/ | Anónimo |

## Precisiones de verificación

- SA-02 y SA-03 describen dos declaraciones para la misma URL, no dos endpoints independientes accesibles a la vez. En la resolución revisada prevalece la vista estándar declarada primero en `server/urls.py`.
- `/media/` figura como configuración del reporte; su servicio HTTP efectivo depende del despliegue y no se confirmó sólo por esa declaración.
- La autenticación no sustituye permisos sobre cada equipo: SA-09 se relaciona con el hallazgo de lectura ajena.
- No todas las rutas tienen una captura individual. Las cuatro figuras generales y las pruebas reproducibles sustentan un avance parcial del inventario.

[Capturas aportadas](evidencias/README.md) · [Resultados de pruebas](../fase-04-owasp-y-priorizacion/evidencias/revision-server5k/README.md)

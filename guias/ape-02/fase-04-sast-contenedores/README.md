# APE 02 · Fase 4 · SAST y contenedores

Revisión del 24/11/2026 sobre el código de Server5K incluido en este portafolio. Se ejecutaron Bandit 1.9.4 sobre `Server5K/app` y `Server5K/server`, y Trivy 0.76.2 sobre la configuración del Dockerfile original y de una propuesta endurecida. El [resumen de Bandit](evidencias/bandit-resumen.json) omite fragmentos de código y credenciales; los [resultados de Trivy](evidencias/trivy-before.json) y [su comparación](evidencias/trivy-after.json) conservan las alertas de configuración. La imagen no se construyó ni se escaneó en este entorno; estos archivos **no** prueban que el contenedor funcione ni que esté libre de vulnerabilidades.

## Sesión 1 · Análisis estático

Bandit revisó 4.151 líneas y reportó **siete alertas: una alta y seis bajas**. El informe aportado menciona seis alertas y 3.819 líneas, correspondientes a otro alcance; aquí se incluyen `app/` y `server/` completos. La severidad indica la regla detectada, no un riesgo explotable confirmado.

| Regla y ubicación | Interpretación | Acción |
| --- | --- | --- |
| B324, alta, `app/utils/idempotency.py:114` | MD5 en la generación de un identificador; la función incluye un timestamp que además impide generar un identificador estable para una misma operación. | Revisar llamadas y propósito; si sigue siendo necesaria, sustituir por SHA-256 con una clave estable por operación y probar los reintentos. |
| B110, baja, `app/views/auth_views.py:75` y `app/websocket/consumers.py:137,446` | Excepciones descartadas con `except: pass`. | Capturar las excepciones esperadas y registrar fallos sin filtrar secretos. |
| B105, baja, `app/tests/tests.py:16` | Contraseña de una prueba. | Mantenerla exclusiva de pruebas; los tests no deben entrar en la imagen final. |
| B311, baja, `app/management/commands/populate_data.py:165` | `random.choice` elige una categoría de datos de ejemplo, no un secreto. | Justificación documentada; no requiere aleatoriedad criptográfica. |
| B105, baja, `server/settings.py:219` | `token_type` es un nombre de claim JWT, no una contraseña. | Falso positivo documentado. |

Para repetirlo desde `Server5K/`: `bandit -r app server -f json -o bandit.json`. Las ubicaciones corresponden a la revisión registrada; pueden variar con cambios posteriores.

## Sesión 2 · Endurecimiento de contenedores

El [Dockerfile propuesto](Dockerfile.hardened) separa la instalación de dependencias de la imagen final, usa UID/GID 10001, mantiene Daphne en el puerto 8000 y define un `HEALTHCHECK` de conectividad local. El archivo original carece de `USER` y `HEALTHCHECK`. Se escanearon ambos archivos con las reglas integradas de Trivy, sin actualización de políticas:

| Control | Original | Propuesta |
| --- | --- | --- |
| DS-0002, alta, proceso como root | Detectado | No detectado |
| DS-0026, baja, sin HEALTHCHECK | Detectado | No detectado |
| Comprobaciones satisfactorias / fallidas | 25 / 2 | 27 / 0 |

La corrección documentada de **DS-0002** consiste en `USER 10001:10001` y permisos de escritura solo para `logs`, `staticfiles` y `mediafiles`. Este resultado valida la configuración del archivo, no la ejecución de la imagen. El `HEALTHCHECK` solo comprueba el puerto, no PostgreSQL ni Redis.

Para adoptar esta propuesta hay que adaptar `Server5K/docker-compose.yml`: seleccionar `Dockerfile.hardened` para `web`, retirar su healthcheck basado en `curl`, restringir `8000` al host local durante el laboratorio y retirar la publicación de `5432` y `6379`; conservar la comunicación interna. Se deben verificar los permisos de los volúmenes con UID 10001 y exigir una contraseña de PostgreSQL y una `SECRET_KEY` seguras. El Compose del proyecto **no se modificó** en esta documentación.

### Pendiente de verificación práctica

1. Construir desde `Server5K/`: `docker build --pull -f ../guias/ape-02/fase-04-sast-contenedores/Dockerfile.hardened -t server5k:ape02-endurecida .` (la ruta es relativa al proyecto; copiar el Dockerfile dentro de `Server5K/` antes de ejecutar si la versión de Docker exige que esté en el contexto).
2. Ejecutar y comprobar UID 10001, `manage.py check`, directorios escribibles, arranque y estado saludable; ajustar Compose antes de levantarlo.
3. Ejecutar `trivy image --scanners vuln --format json --output trivy-image.json server5k:ape02-endurecida`. Registrar CVE, paquete, versión, corrección o justificación y repetir el escaneo.
4. Guardar el registro de construcción, el reporte de escaneo y capturas reales sin `.env`, contraseñas ni tokens. Hasta entonces no debe marcarse como terminada la actividad de construcción y escaneo de imagen.

## Portafolio de la Unidad 1

[APE 01](../../ape-01/README.md) documenta superficie, activos, errores y priorización OWASP. En APE 02, la [Fase 2](../fase-02-control-acceso/sesion-02-idor/README.md) conserva pruebas JWT e IDOR y la [Fase 3](../../../APE02/Fase03/README.md) contiene SQLi y XSS en DVWA y Server5K. Este apartado registra la Fase 4 hasta el alcance comprobado. El PDF aportado reúne varios avances, pero presenta duplicaciones y declara pendiente el escaneo de imagen; por ello el índice enlaza evidencias puntuales en vez de presentarlo como cierre verificado.

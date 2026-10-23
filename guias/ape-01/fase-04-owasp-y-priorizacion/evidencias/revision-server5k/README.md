# Evidencias de revisión local de Server5K

Fecha de revisión: 21 de octubre de 2026 (America/Guayaquil).
Marca de ejecución del proceso: `2026-10-21T13:28:36.537094+00:00`.
Código: `826aec5c04dfc5d3f8be77e9abde2d13f69a51e8`; Django instalado: `5.2.8`.

## Archivos

- [resultados-pruebas.json](resultados-pruebas.json): 19 comprobaciones, con respuestas y estados; datos sintéticos.
- [reproducir_pruebas.py](reproducir_pruebas.py): procedimiento ejecutable de las comprobaciones.
- [dependencias-instaladas.txt](dependencias-instaladas.txt): inventario de paquetes del entorno instalado.
- [pip-audit.json](pip-audit.json): salida original del escáner; contiene registros repetidos y alias, por lo que el número bruto de avisos no equivale a vulnerabilidades únicas ni explotables.

## Reproducir

Desde el repositorio de evidencias:

```bash
/home/joseph/Documentos/Servidor5KAuditar/Server5K/.venv/bin/python \
  guias/ape-01/fase-04-owasp-y-priorizacion/evidencias/revision-server5k/reproducir_pruebas.py \
  /home/joseph/Documentos/Servidor5KAuditar/Server5K > /tmp/resultados-server5k.json
```

El script usa una clave aleatoria, una base SQLite temporal y Channels en memoria. No carga `.env`, no usa Redis ni PostgreSQL reales y elimina su base temporal al finalizar. Django puede crear el directorio de logs al importar su configuración; el log de las pruebas se redirige al directorio temporal. Las respuestas de páginas DEBUG completas no se guardan para evitar copiar información sensible. La salida por stderr contiene advertencias y errores controlados de prueba.

La comprobación XSS cambia únicamente el almacenamiento de archivos estáticos durante esa solicitud para no depender de un manifiesto de `collectstatic`; mantiene el escape HTML de las plantillas.

El escáner se ejecutó fuera del entorno de la aplicación:

```bash
.tools/uv tool run --from pip-audit pip-audit \
  -r /tmp/server5k-audit-installed.txt --no-deps --disable-pip \
  --format json --output /tmp/server5k-pip-audit.json
```

Para repetir, sustituir las rutas `/tmp` por el inventario y archivo de salida deseados. `--no-deps` se utilizó porque el inventario incluye todos los paquetes instalados. La consulta comunica nombres y versiones de paquetes al servicio de avisos de seguridad. No remite el código fuente ni credenciales.

## Límites

Estas evidencias son pruebas de componentes mediante APIClient y WebsocketCommunicator, no capturas del navegador ni tráfico contra un despliegue real. No verifican configuración de proxy, TLS público, contención concurrente en PostgreSQL ni Redis real. El caso de la clave pública de fallback se prueba sólo bajo una configuración simulada; no se afirma que la clave local sea esa.

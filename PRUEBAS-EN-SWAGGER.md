# Pruebas visuales en Swagger

Laboratorio local preparado el 23/10/2026. Usa SQLite separado, Channels en memoria y datos ficticios. No usa la base real. Se añadió documentación del cuerpo de registros en memoria para que Swagger permita editarlo; la lógica de validación y persistencia sigue siendo la del proyecto.

## Página y acceso

http://127.0.0.1:8000/api/docs/

POST /api/login/ → Try it out → usar:

```json
{"username":"juez_demo_a","password":"Laboratorio5K!2026"}
```

Execute → copiar sólo access → Authorize → pegar el token sin la palabra Bearer → Apply credentials → Close.

Son credenciales públicas de este laboratorio local, no de una cuenta real.

## A06 reproducido desde la web

POST /api/equipos/{equipo_id}/registros/ → Try it out → equipo_id = 3.

Cuerpo enviado:

```json
{"registros":[
 {"tiempo":-1000},{"tiempo":-1000},{"tiempo":-1000},
 {"tiempo":-1000},{"tiempo":-1000},{"tiempo":-1000},
 {"tiempo":-1000},{"tiempo":-1000},{"tiempo":-1000},
 {"tiempo":-1000},{"tiempo":-1000},{"tiempo":-1000},
 {"tiempo":-1000},{"tiempo":-1000},{"tiempo":-1000}
]}
```

Resultado observado en Swagger: HTTP 201, exito true, equipo LAB Negativos, total_guardados 15 y tiempo -1000 en los registros devueltos. La aplicación debería rechazar tiempos negativos con 400 y no guardarlos.

**El equipo 3 ya tiene esos registros.** Repetir la solicitud sin reiniciar devuelve 400 por registros previos y no contradice la evidencia inicial. Para repetir desde cero, detener sólo el proceso del laboratorio y arrancarlo otra vez: crea una base nueva.

## Reiniciar el laboratorio

Cuando el puerto 8000 esté libre:

```bash
cd /home/joseph/Documentos/Servidor5KAuditar/Server5K-Seguridad
../Server5K/.venv/bin/python herramientas/iniciar_swagger_lab.py
```

Mantener esa terminal abierta; Ctrl+C detiene el laboratorio. No ejecutar una segunda instancia sobre el mismo puerto. Al reiniciar se regeneran la clave y los datos y hace falta volver a iniciar sesión y autorizar Swagger. El título de Swagger puede seguir mostrando Server5K API; la base de este proceso es la del laboratorio separado. El script imprime su directorio temporal al arrancar.

Equipos del laboratorio: 1 propio, 2 de otro juez, 3 prueba negativa, 4 lote parcial, 5 de competencia detenida. Ambos jueces son ficticios. Nunca publicar tokens reales.

## A08 y A09

A08 no se demuestra con un endpoint: revisar Dockerfile:26 para la referencia uv:latest sin digest. No se confirmó manipulación de software.

A09: desde Swagger se pueden provocar rechazos de login usando la contraseña incorrecta de esta cuenta ficticia; para evaluar su registro hay que observar también el django.log del directorio LAB_DIR impreso por el proceso. Un 401 o 200 en Swagger, por sí solo, no demuestra la calidad de los logs ni la presencia de alertas. Conservar las limitaciones de la revisión del código.

## Única captura

[EVI-A06-swagger-tiempo-negativo.jpg](guias/ape-01/fase-04-owasp-y-priorizacion/evidencias/revision-server5k/EVI-A06-swagger-tiempo-negativo.jpg)

Pie sugerido: «A06: en laboratorio local aislado, POST /api/equipos/3/registros/ respondió 201 y aceptó 15 tiempos negativos. La captura muestra la URL y el valor -1000 devuelto por la API. Fecha: 23/10/2026».

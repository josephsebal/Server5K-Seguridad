# Respuestas y hallazgos — Práctica OWASP Top 10:2025

Aplicación: Server5K. Fecha: 21/10/2026. Estudiantes: completar con los integrantes.

Respuestas propuestas para estudiar y adaptar a la entrega. El estado de las simulaciones del navegador no fue modificado ni se afirma haberlas completado. Los hallazgos se basan en la revisión de Server5K, no en las simulaciones de juguete.

## A01

**Pregunta:** Si un usuario puede ver la factura de otro cambiando sólo el número de la dirección, ¿qué control falta y en qué capa debe vivir?

**Respuesta:** Falta autorización sobre el objeto: comprobar que la factura pertenece al usuario autenticado o que su rol permite consultarla. Debe ejecutarse en el backend en cada petición; ocultar botones en el frontend no impide cambiar la URL. En Server5K falta esa comprobación en el estado de registros del equipo, aunque sí existe en otras rutas.

**Hallazgo o resultado en mi aplicación:** **Estado: Hallazgo confirmado; otros controles funcionan.** En `GET /api/equipos/2/registros/estado/` pude consultar los registros de un equipo ajeno usando el token de otro juez. En `app/views/registro_views.py`, `EstadoEquipoRegistrosView.get`, se obtiene el equipo por ID sin comprobar el juez propietario. La respuesta fue 200 con los registros; el detalle `/api/equipos/2/` sí devolvió 404. Existe una inconsistencia de autorización. Como parte de los resultados es pública, debe confirmarse qué información de este endpoint debe ser privada». Ver [ruta, archivo, prueba y evidencia de A01](registro-detallado-por-categoria.md#a01--control-de-acceso-roto).

## A02

**Pregunta:** Menciona dos piezas de información que regala una cabecera como X-Powered-By y explica por qué ayuda a un atacante.

**Respuesta:** Puede revelar la tecnología o framework usado y su versión, si está incluida; por ejemplo PHP y 7.4.2. Sirven para identificar la plataforma y buscar fallos conocidos aplicables a esa versión. La cabecera por sí sola no demuestra que exista una vulnerabilidad explotable y ocultarla no sustituye actualizar el software.

**Hallazgo o resultado en mi aplicación:** **Estado: Riesgo condicionado al modo DEBUG; controles positivos en cabeceras.** En `POST /api/login/`, enviar una lista JSON mientras `DEBUG=True` expone una traza y rutas internas. El comportamiento se origina en `app/views/auth_views.py:59` y depende de `server/settings.py:16`. Es un riesgo de configuración si se publica el modo de depuración; no confirmé esa exposición en producción. Las cabeceras X-Frame-Options, X-Content-Type-Options y Referrer-Policy sí estuvieron presentes en la respuesta revisada». Ver [ruta, archivo, prueba y evidencia de A02](registro-detallado-por-categoria.md#a02--configuración-insegura).

## A03

**Pregunta:** ¿Por qué puede haber código vulnerable que ningún integrante escribió? ¿Qué herramienta lo revisa en la Guía 04?

**Respuesta:** Porque la aplicación incorpora dependencias directas, transitivas, imágenes y herramientas de terceros. Sus fallos también forman parte del sistema. La práctica señala Trivy en GitHub Actions como escáner SCA y control del pipeline de la Guía 04. Un escáner detecta versiones asociadas a avisos; después hay que evaluar si el código vulnerable es alcanzable.

**Hallazgo o resultado en mi aplicación:** **Estado: Versiones con avisos confirmadas; explotabilidad de cada CVE pendiente.** Revisé `.venv`, `uv.lock`, `requirements.txt` y `Dockerfile`. Encontré Django 5.2.8 instalado y avisos de seguridad en 17 paquetes mediante pip-audit; además, requirements fija Django 6.0 y el lock fija 5.2.8. Hay dependencias por actualizar y entornos que pueden resolver versiones distintas. No comprobé explotación de cada CVE desde una ruta de la aplicación». Ver [ruta, archivo, prueba y evidencia de A03](registro-detallado-por-categoria.md#a03--fallos-de-cadena-de-suministro).

## A04

**Pregunta:** ¿Por qué MD5 sirve para verificar una descarga, pero no para guardar contraseñas?

**Respuesta:** MD5 es rápido: puede comparar una huella para detectar corrupción accidental, pero esa rapidez permite probar muchas contraseñas por segundo. MD5 sin sal tampoco evita reutilizar tablas precalculadas. Para contraseñas se necesita una función específica con sal y coste ajustable, como Argon2id o una configuración adecuada de PBKDF2/bcrypt. MD5 tiene además colisiones conocidas: para descargas sometidas a un atacante se debe usar SHA-256 desde una fuente auténtica o una firma digital, no confiar en MD5 como garantía de autenticidad.

**Hallazgo o resultado en mi aplicación:** **Estado: Hash de contraseñas protegido en la prueba; riesgo JWT condicional.** En `app/models/juez.py`, las contraseñas se almacenan usando PBKDF2-SHA256 con sal mediante las funciones de Django: el control de almacenamiento funcionó. Sin embargo, `server/settings.py:13` define una clave pública de respaldo que también firma JWT; al simular ese despliegue, un token firmado con ella accedió a `/api/me/` (200). El riesgo existe si no se configura SECRET_KEY; no se confirmó en la configuración local actual». Ver [ruta, archivo, prueba y evidencia de A04](registro-detallado-por-categoria.md#a04--fallos-criptográficos).

## A05

**Pregunta:** ¿Qué hace cada parte del payload ' OR 1=1 -- y qué control lo detiene?

**Respuesta:** En una consulta vulnerable que concatena datos dentro de comillas, la comilla intenta cerrar el literal, OR 1=1 introduce una condición siempre verdadera y -- intenta comentar el resto de la sentencia, según la sintaxis del motor. El efecto depende de cómo se construya la consulta. Las consultas parametrizadas separan datos de instrucciones; no se debe concatenar la entrada. Validar y escapar según contexto complementa ese control.

**Hallazgo o resultado en mi aplicación:** **Estado: Controles efectivos en los flujos probados; sin inyección confirmada.** En `POST /api/login/`, el texto SQL de prueba no permitió iniciar sesión y respondió 401; la consulta usa filtros ORM en `app/views/auth_views.py`. En `/equipo/6/`, `templates/app/equipo_detail.html` escapó el marcador HTML del nombre del equipo. No encontré SQLi ni XSS en esos flujos: los controles funcionaron en las pruebas realizadas. No se puede afirmar que toda la aplicación esté libre de inyecciones». Ver [ruta, archivo, prueba y evidencia de A05](registro-detallado-por-categoria.md#a05--inyección).

## A06

**Pregunta:** ¿Por qué el camino A era explotable aunque el código no tenía errores?

**Respuesta:** Porque implementaba correctamente una regla de recuperación insegura: conocer una respuesta pública, como el nombre de una mascota, no demuestra la identidad. El problema estaba en el requisito y el modelo de confianza. Se debe rediseñar con un token aleatorio de un solo uso, vencimiento, canal verificado y límites de solicitudes.

**Hallazgo o resultado en mi aplicación:** **Estado: Hallazgos de integridad de negocio confirmados.** En `POST /api/equipos/3/registros/` se guardaron 15 tiempos de -1000 ms (201) porque `app/services/registro_service.py` no valida el rango. En `/api/equipos/5/registros/` pude guardar tiempos en una competencia detenida al tener otro equipo en una activa: `registro_views.py:100` y `registro_service.py:204` validan la competencia del primer equipo, no la del solicitado. Son fallos de reglas de negocio e integridad». Ver [ruta, archivo, prueba y evidencia de A06](registro-detallado-por-categoria.md#a06--diseño-inseguro).

## A07

**Pregunta:** ¿Qué tres capas fortalecen la autenticación y qué categoría registra los intentos fallidos?

**Respuesta:** MFA, limitación de intentos con demora o bloqueo temporal y gestión segura de sesiones: cookies HttpOnly/Secure/SameSite cuando correspondan, expiración y revocación definidas. La categoría hermana es A09: Security Logging and Alerting Failures, que cubre el registro y la alerta ante intentos sospechosos.

**Hallazgo o resultado en mi aplicación:** **Estado: Hallazgos confirmados en login y política del formulario.** En `POST /api/login/` se permitieron seis intentos fallidos seguidos sin espera ni bloqueo visible; no hay throttle en la vista ni en settings. En `app/admin.py`, `JuezAdminForm.clean` aceptó la contraseña 123 porque sólo verifica obligatoriedad y coincidencia. Se comprobó la clase del formulario que usa `/admin/app/juez/add/`, no un alta administrativa por navegador. Hay fallos de limitación de intentos y aplicación de la política de contraseñas». Ver [ruta, archivo, prueba y evidencia de A07](registro-detallado-por-categoria.md#a07--fallos-de-autenticación).

## A08

**Pregunta:** Si un instalador cambia un byte durante la descarga, ¿qué ocurre con SHA-256 y qué decide el usuario?

**Respuesta:** La huella SHA-256 calculada será distinta con probabilidad abrumadora; un cambio mínimo suele alterar muchos bits del resultado. Si no coincide con el hash de una fuente auténtica, se debe rechazar el archivo, no ejecutarlo y volver a obtenerlo de una fuente verificada. Si un atacante también puede sustituir el hash publicado, la comparación sola no autentica el archivo; una firma verificada aporta esa garantía.

**Hallazgo o resultado en mi aplicación:** **Estado: Flujos de la simulación no aplicables al módulo revisado; endurecimiento pendiente.** No aplica la prueba del instalador o actualizador a un módulo propio identificado en Server5K: no encontré esa funcionalidad dentro del alcance. Tampoco confirmé deserialización insegura. En la construcción sí observé `Dockerfile:26` con uv:latest sin digest, por lo que recomiendo fijar su integridad; esta observación se registra en A03 para no duplicar el mismo hallazgo. La categoría general no se declara completamente segura». Ver [ruta, archivo, prueba y evidencia de A08](registro-detallado-por-categoria.md#a08--fallos-de-integridad-de-software-o-datos).

## A09

**Pregunta:** ¿Qué tres preguntas responde una bitácora que una pantalla vacía no puede?

**Respuesta:** Quién realizó la acción, cuándo ocurrió y desde dónde se originó, por ejemplo la IP obtenida de una cadena de proxy confiable. Para investigar también conviene registrar qué hizo, sobre qué recurso y con qué resultado, usando un identificador de correlación y sin guardar contraseñas o tokens.

**Hallazgo o resultado en mi aplicación:** **Estado: Cobertura insuficiente de auditoría de autenticación.** Al probar `POST /api/login/`, los rechazos generaron Unauthorized sin identidad del intento ni origen. En `app/views/auth_views.py` no hay registro estructurado de login exitoso/fallido y en el código revisado no identifiqué alertas por repetición. El problema es cobertura insuficiente de auditoría; no ausencia total de logs. No evalué monitoreo externo». Ver [ruta, archivo, prueba y evidencia de A09](registro-detallado-por-categoria.md#a09--fallos-de-registro-y-alerta).

## A10

**Pregunta:** ¿Adónde va el detalle técnico cuando se muestra un mensaje genérico y por qué es mejor?

**Respuesta:** Al registro interno del servidor, con acceso restringido y un código de correlación que el usuario pueda comunicar a soporte. Así el equipo conserva los datos necesarios para diagnosticar sin entregar rutas, consultas o trazas al cliente. La aplicación debe responder con estado seguro y hacer rollback cuando la operación requiera atomicidad.

**Hallazgo o resultado en mi aplicación:** **Estado: Hallazgos confirmados; algunos errores sí se manejan correctamente.** En `POST /api/login/`, una lista JSON produjo 500 por usar `.get()` sin validar el objeto. En `/api/equipos/1/registros/`, un número en registros produjo 500 y una lista de cadenas expuso un AttributeError en texto. En `/api/equipos/4/registros/`, un lote con 14 errores guardó sólo un tiempo (201) y luego impidió completar el equipo (400). Las causas están en `auth_views.py`, `registro_views.py` y `registro_service.py`. Hay validación incompleta y recuperación inconsistente de errores». Ver [ruta, archivo, prueba y evidencia de A10](registro-detallado-por-categoria.md#a10--excepciones-y-errores-mal-gestionados).

## Evidencias y fuentes

- [Informe técnico con causas y correcciones](hallazgos-server5k.md).
- [Resultados y procedimiento reproducible](evidencias/revision-server5k/README.md).
- [Lista oficial OWASP Top 10:2025](https://top10.owasp.org/2025/).
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
- [OWASP Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).
- [Aviso oficial Django para los ejemplos de dependencias](https://www.djangoproject.com/weblog/2025/dec/02/security-releases/).

# Revisión OWASP de Server5K

Fecha: 21 de octubre de 2026. Commit analizado: `826aec5c04dfc5d3f8be77e9abde2d13f69a51e8`.

## Resultado y alcance

Se documentan diez hallazgos: ocho observados en componentes/código de la aplicación (HAL-001–007 y HAL-010), un riesgo crítico condicionado a la configuración (HAL-008) y un hallazgo de dependencias/configuración de construcción cuya explotabilidad por CVE requiere análisis (HAL-009). No todos equivalen a un ataque explotable en producción.

La revisión comprende código, 19 comprobaciones reproducibles con datos sintéticos, validación del formulario administrativo, API REST, dos controles WebSocket y SCA de la instalación Python. Se usó SQLite temporal y Channels en memoria; **no se utilizó la base real ni se modificó el código funcional de Server5K**. No se evaluó un sitio público, un proxy, la aplicación móvil ni concurrencia de PostgreSQL. El cliente de pruebas no comprueba por defecto CSRF: no se deduce una vulnerabilidad CSRF de esas solicitudes.

Las categorías corresponden a [OWASP Top 10:2025](https://top10.owasp.org/2025/). El Top 10 orienta la clasificación; la matriz utiliza una escala de trabajo, no una puntuación CVSS.

## Detalle de hallazgos

### HAL-001 — Lectura de registros de un equipo ajeno

- **Categoría:** A01:2025. **Severidad estimada:** Media.
- **Estado:** Confirmado en prueba aislada.
- **Código:** `app/views/registro_views.py:203–218` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P01-IDOR / P02-ANON; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** Un juez A consulta `/api/equipos/2/registros/estado/` de un equipo asignado al juez B. Obtiene HTTP 200 con UUID, tiempos y estado de envío. La ruta de detalle `/api/equipos/2/` responde 404 y la misma consulta sin autenticación responde 401.

**Causa e impacto:** Se exige autenticación, pero `Equipo.objects.get(id=equipo_id)` no filtra por juez. Se rompe el aislamiento entre jueces de esa API. Los resultados tienen vistas públicas: no se ha demostrado exposición de datos personales ni escritura ajena; confirmar la política de privacidad del endpoint para valorar el impacto final.

**Corrección recomendada:** Filtrar por `judge_id=request.user.id` al recuperar el equipo, o comprobar un permiso de objeto explícito. Conservar 404/403 para equipos ajenos y añadir una prueba de regresión con dos jueces.


### HAL-002 — Login sin limitación de intentos en la aplicación

- **Categoría:** A07:2025. **Severidad estimada:** Alta.
- **Estado:** Confirmado en código y prueba acotada.
- **Código:** `app/views/auth_views.py:15–98; server/settings.py:169–176` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P03-LOGIN; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** Seis intentos fallidos consecutivos devuelven 401 y el siguiente intento correcto devuelve 200; no se produjo espera ni bloqueo. DRF no configura clases de throttling y la vista no define limitadores.

**Causa e impacto:** Facilita intentos de adivinación y reutilización de credenciales. Se requieren una cuenta objetivo y contraseñas acertadas; no se ejecutó fuerza bruta. Un proxy de producción podría agregar protección y no fue examinado.

**Corrección recomendada:** Agregar límites por cuenta e IP, demora progresiva, alertas y MFA para perfiles sensibles. Evitar bloqueos permanentes que permitan denegar acceso a otros usuarios.


### HAL-003 — El formulario de jueces acepta contraseñas débiles

- **Categoría:** A07:2025. **Severidad estimada:** Alta.
- **Estado:** Confirmado en validación del formulario.
- **Código:** `app/admin.py:318–345; app/models/juez.py:25–31` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P04-WEAK-PASSWORD; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** `JuezAdminForm` considera válida la contraseña sintética `123` y su confirmación, aunque existen cuatro validadores de contraseña en settings.

**Causa e impacto:** La validación personalizada sólo comprueba que haya contraseña y que ambas coincidan. `set_password()` aplica hash pero no ejecuta la política. Crear un juez requiere acceso administrativo; no es registro anónimo ni exposición de contraseñas en texto plano.

**Corrección recomendada:** Invocar `django.contrib.auth.password_validation.validate_password()` desde el formulario y las demás rutas de alta/cambio. Mantener make_password/check_password, contraseñas únicas y eliminar claves predecibles en aprovisionamiento productivo.


### HAL-004 — Tiempos negativos persistidos por el endpoint HTTP

- **Categoría:** A06:2025. **Severidad estimada:** Alta.
- **Estado:** Confirmado en prueba aislada.
- **Código:** `app/services/registro_service.py:262–299; app/views/registro_views.py:122–126` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P05-NEGATIVE; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** El juez asignado envía 15 objetos con `tiempo: -1000`. Recibe 201 y se guardan 15 tiempos negativos.

**Causa e impacto:** La ruta activa HTTP usa un servicio que no aplica `RegistroTiempoSerializer` ni valida los valores de negocio. Los validadores de un serializer que no se usa no protegen este flujo. Se compromete la integridad de los resultados.

**Corrección recomendada:** Validar la lista completa con un serializer: tiempo entero, no negativo, límite máximo y coherencia entre tiempo y componentes. Mantener las mismas reglas en todos los transportes y añadir restricciones de base de datos cuando corresponda.


### HAL-005 — Un lote incompleto se guarda y bloquea el reenvío

- **Categoría:** A10:2025. **Severidad estimada:** Media.
- **Estado:** Confirmado en prueba aislada.
- **Código:** `app/services/registro_service.py:246–269,295–322; app/views/registro_views.py:138–153` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P06-PARTIAL; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** Un lote de longitud 15 con un tiempo válido y 14 objetos vacíos responde 201 y guarda sólo un registro. Un reenvío válido de 15 tiempos responde 400 porque el equipo ya tiene un registro.

**Causa e impacto:** Aunque se utiliza `transaction.atomic()`, los elementos inválidos se omiten sin abortar el lote. Esto incumple la promesa de guardar exactamente 15 tiempos de forma atómica y puede impedir completar el equipo sin intervención.

**Corrección recomendada:** Validar todo el lote antes de persistir y rechazarlo íntegramente si un elemento falla. Definir reintento e idempotencia y permitir recuperación controlada sin perder trazabilidad.


### HAL-006 — Se permite escribir tiempos en una competencia detenida

- **Categoría:** A06:2025. **Severidad estimada:** Alta.
- **Estado:** Confirmado en prueba aislada.
- **Código:** `app/views/registro_views.py:99–119; app/services/registro_service.py:203–207` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P07-CLOSED-COMPETITION; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** Un juez tiene un primer equipo en una competencia activa y otro en una detenida/inactiva. Envía 15 tiempos al segundo equipo; recibe 201 y los 15 registros se guardan.

**Causa e impacto:** La validación usa la competencia del primer equipo del juez, en vez de `equipo.competition` del objetivo. Se requiere que el juez tenga equipos en más de una competencia y que el primero cumpla el estado; permite alterar resultados fuera de la ventana autorizada.

**Corrección recomendada:** Recuperar primero el equipo objetivo, validar pertenencia y después el estado de su competencia dentro de la transacción. Definir explícitamente la regla para is_active/is_running y probar asignaciones en competencias diferentes.


### HAL-007 — Tipos JSON incorrectos provocan 500 o filtran detalles internos

- **Categoría:** A10:2025. **Severidad estimada:** Media.
- **Estado:** Confirmado; trazas completas sólo con DEBUG=True.
- **Código:** `app/views/auth_views.py:59–60; app/views/registro_views.py:74–84; app/services/registro_service.py:265–266,326–336` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P09-LOGIN-LIST / P10-BATCH-TYPE / P11-BATCH-ITEMS / P13-DEBUG; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** Un JSON raíz tipo lista en login devuelve 500. `registros: 15` devuelve 500. Una lista de 15 cadenas devuelve 400 con `Error general: 'str' object has no attribute 'get'`. Con DEBUG=True la primera solicitud muestra traceback y ruta del proyecto; con DEBUG=False el 500 es genérico.

**Causa e impacto:** Falta validación de estructura previa a `.get()`/`len()` y se devuelven excepciones de implementación. Un 500 por una petición no demuestra una caída del servicio ni denegación de servicio sostenida. Las trazas DEBUG son un riesgo si el entorno de desarrollo se expone.

**Corrección recomendada:** Usar serializers para objeto raíz, listas e ítems; responder 400 con mensajes de campo. Reservar excepciones y traceback al log interno con referencia de soporte. Mantener DEBUG=False en producción.


### HAL-008 — Clave JWT pública de fallback si falta SECRET_KEY

- **Categoría:** A04:2025. **Severidad estimada:** Crítica condicional.
- **Estado:** Código confirmado y escenario simulado; no afecta por defecto al .env local.
- **Código:** `server/settings.py:13,210` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P17-DEFAULT-SIGNING; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** Cuando se simula ausencia de una clave configurada y se usa la constante pública del código para firmar JWT, un token creado con ella permite consultar `/api/me/` (200) como el juez de prueba.

**Causa e impacto:** La constante conocida se reutiliza como SIGNING_KEY. La explotación requiere un despliegue que efectivamente use ese fallback. El .env local contiene una clave configurada y no se publican su valor ni tokens; no se afirma compromiso de ese entorno.

**Corrección recomendada:** Fallar durante el arranque si falta la clave o es insegura; usar un secreto aleatorio por entorno y rotarlo si se utilizó el fallback. Invalidar los tokens firmados con una clave comprometida.


### HAL-009 — Dependencias instaladas con avisos y fuentes de versiones divergentes

- **Categoría:** A03:2025. **Severidad estimada:** Alta potencial.
- **Estado:** SCA y revisión de archivos; explotación por CVE no demostrada.
- **Código:** `uv.lock:364–365; requirements.txt:46; Dockerfile:26,35` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** pip-audit.json / dependencias-instaladas.txt; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** El entorno instalado usa Django 5.2.8 y el escáner reporta avisos en 17 paquetes. El lock fija Django 5.2.8, pero requirements.txt fija 6.0 y Docker instala desde requirements.txt. Además se copia uv desde una etiqueta `latest`.

**Causa e impacto:** El entorno local auditado y una construcción Docker pueden usar versiones diferentes. Un ejemplo verificado con fuente oficial es CVE-2025-13372, corregido en Django 5.2.9; afecta condiciones específicas de FilteredRelation/annotate/alias en PostgreSQL, que no se demostraron accesibles en Server5K. No se extrapola a SQLi en el login.

**Corrección recomendada:** Unificar la fuente de resolución, actualizar a versiones soportadas y corregidas con pruebas, regenerar lock/exportación y ejecutar SCA en CI. Revisar alcance de cada aviso, separar herramientas de desarrollo y fijar imágenes/herramientas por digest.


### HAL-010 — Autenticación sin eventos de auditoría con identidad y alertas

- **Categoría:** A09:2025. **Severidad estimada:** Media.
- **Estado:** Revisión estática y observación limitada de logs.
- **Código:** `app/views/auth_views.py:55–98; server/settings.py:279–320` del repositorio objetivo, commit indicado arriba.
- **Evidencia:** P03-LOGIN; [resultados y procedimiento](evidencias/revision-server5k/README.md).

**Reproducción y resultado:** La vista de login no registra éxito/fallo con identidad, IP o ID de correlación. En seis rechazos se capturó el mensaje genérico `Unauthorized: /api/login/`, sin el contexto del intento; no hay alerta de repetición identificada en el código.

**Causa e impacto:** Sí hay registros del framework y del WebSocket: no se afirma que no existan logs. La carencia es de eventos estructurados de autenticación y de un mecanismo de alerta visible en este repositorio. Un servicio externo de monitoreo no fue examinado.

**Corrección recomendada:** Emitir eventos de autenticación con hora, resultado, identificador de cuenta, origen confiable e ID de correlación; proteger acceso y retención y alertar ante patrones. No registrar contraseñas, tokens ni cookies completas.

## Observaciones y controles positivos

- **A02:** `.env` local tiene DEBUG=True y HTTPS deshabilitado, coherente con la instalación de desarrollo preparada antes. No se considera vulnerabilidad de producción sin comprobar despliegue/exposición. P13 demuestra qué ocurriría si se expone ese modo. No se observó `X-Powered-By` porque no se examinó un servidor HTTP real.
- **A04:** los jueces usan `pbkdf2_sha256` con sal a través de make_password/check_password; no se encontró MD5 ni texto plano en el modelo para almacenamiento de contraseñas. Los comandos de población generan ficheros de credenciales legibles: protegerlos y no publicarlos; no se comprobó que existan en el despliegue.
- **A05:** la entrada SQL de prueba recibió 401 y un nombre con marcador `<script>` se mostró escapado en la vista HTML (P15/P16). No se confirmó SQLi ni XSS en esos flujos. Es una comprobación limitada, no prueba de ausencia global. Los avisos CVE de dependencias se registran en A03 hasta analizar su alcance.
- **A08:** se recomienda fijar herramientas e imágenes por digest; `@v4` es una etiqueta movible, no equivale a fijar el SHA completo de un commit. No se identificó un flujo propio de actualización o deserialización insegura explotable. La observación de `uv:latest` se agrupa en HAL-009 para no duplicar hallazgos.
- **Permisos:** el detalle de equipo ajeno devuelve 404; el estado sin token devuelve 401; WebSocket rechaza ausencia de token y discrepancia de juez (P02/P18/P19).
- **Errores:** login sin campos responde 400 y refresh con tipo incorrecto responde 400 por validación de SimpleJWT (P08/P12). El router resuelve `/api/token/refresh/` con la vista estándar declarada primero en `server/urls.py`; no se atribuye automáticamente a la vista custom de igual ruta.
- **Cabeceras:** P14 observó `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` y `Referrer-Policy: same-origin`. Ausencia de CSP en esa muestra es una oportunidad de defensa, no XSS demostrado. HSTS y cookies Secure dependen de un despliegue HTTPS que no fue probado.
- **Datos públicos:** el endpoint de estado de competencias es público por diseño según el código. Sin política de negocio que restrinja sus datos, no se declara automáticamente un bypass administrativo.

## Fuentes

- [Lista oficial OWASP Top 10:2025](https://top10.owasp.org/2025/).
- [Aviso oficial Django del 2 de diciembre de 2025](https://www.djangoproject.com/weblog/2025/dec/02/security-releases/): confirma los ejemplos CVE-2025-13372 y CVE-2025-64460 y sus condiciones; no implica que la aplicación utilice los caminos afectados.
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
- [OWASP Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).

Las propuestas no se aplicaron al código: quedan para una fase de corrección y nueva verificación.

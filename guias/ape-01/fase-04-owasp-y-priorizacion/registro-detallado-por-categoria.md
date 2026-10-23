# Registro detallado para la actividad OWASP — Server5K

Fecha: 21/10/2026. Aplicación: `/home/joseph/Documentos/Servidor5KAuditar/Server5K/`.

## Cómo interpretar los resultados

- **Hallazgo confirmado:** resultado observado en pruebas aisladas, con evidencia.
- **Control efectivo en lo probado:** la defensa funcionó en ese flujo; no certifica toda la categoría.
- **No aplica al flujo:** la funcionalidad específica de la simulación no se identificó en el módulo revisado.
- **Condicionado / pendiente:** depende de una configuración o de un despliegue no evaluado; no presentarlo como explotación actual.

Se detallan las comprobaciones ya ejecutadas; esta ampliación no agrega nuevas pruebas. Las solicitudes se resolvieron internamente con APIClient/WebsocketCommunicator, **no contra un servidor en localhost ni contra producción**. Los IDs 1–6 pertenecen a la base temporal creada por el procedimiento y pueden ser distintos en tu instalación. Para pruebas manuales hay que sustituirlos por los IDs de las cuentas y equipos de laboratorio. Si el servidor se ejecuta localmente, la base habitual es `http://127.0.0.1:8000`; no se comprobó en esta revisión que esté encendido.

Las rutas de archivo que siguen son relativas al directorio de Server5K indicado arriba. El formulario de jueces se probó directamente, por lo que no se le atribuye una respuesta HTTP de alta por navegador.

## A01 — Control de acceso roto

**Estado:** Hallazgo confirmado; otros controles funcionan.

**Ruta o componente:** `GET /api/equipos/2/registros/estado/`, autenticado como juez A; el equipo 2 pertenece al juez B. Comparación: `GET /api/equipos/2/` y la consulta de estado sin token.

**Archivo del proyecto:** `app/views/registro_views.py:203` (`EstadoEquipoRegistrosView.get`), especialmente línea 207. Control positivo: `app/views/equipo_views.py`, método `get_queryset`.

**Qué probé:** Se crearon dos jueces y sus equipos. Con el token de A se solicitó el estado del equipo de B. Se repitió la consulta sin token y se consultó el detalle del mismo equipo.

**Qué encontré:** El estado devolvió **200** con nombre del equipo, UUID y tiempos de B. El detalle devolvió **404** y sin token se recibió **401**. La consulta por ID no filtra `judge_id`.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«En `GET /api/equipos/2/registros/estado/` pude consultar los registros de un equipo ajeno usando el token de otro juez. En `app/views/registro_views.py`, `EstadoEquipoRegistrosView.get`, se obtiene el equipo por ID sin comprobar el juez propietario. La respuesta fue 200 con los registros; el detalle `/api/equipos/2/` sí devolvió 404. Existe una inconsistencia de autorización. Como parte de los resultados es pública, debe confirmarse qué información de este endpoint debe ser privada».

**Evidencia y límites:** P01-IDOR y P02-ANON. **No implica permiso para modificar equipos ajenos**; sólo se confirmó lectura de esa ruta.

## A02 — Configuración insegura

**Estado:** Riesgo condicionado al modo DEBUG; controles positivos en cabeceras.

**Ruta o componente:** `POST /api/login/` con JSON raíz `[]` y `DEBUG=True`. Cabeceras: `GET /audit-no-existe/` con `DEBUG=False`.

**Archivo del proyecto:** `server/settings.py:16` (`DEBUG`) y `app/views/auth_views.py:59` (`request.data.get`).

**Qué probé:** Se envió una lista en lugar del objeto JSON esperado al login bajo ambas configuraciones de depuración. Se revisaron las cabeceras de una respuesta 404.

**Qué encontré:** Con DEBUG=True: **500** con traceback, AttributeError y ruta del proyecto. Con DEBUG=False: **500 genérico** sin esos detalles. La respuesta 404 incluyó DENY, nosniff y same-origin. El `.env` local está preparado para desarrollo, no se probó un despliegue público.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«En `POST /api/login/`, enviar una lista JSON mientras `DEBUG=True` expone una traza y rutas internas. El comportamiento se origina en `app/views/auth_views.py:59` y depende de `server/settings.py:16`. Es un riesgo de configuración si se publica el modo de depuración; no confirmé esa exposición en producción. Las cabeceras X-Frame-Options, X-Content-Type-Options y Referrer-Policy sí estuvieron presentes en la respuesta revisada».

**Evidencia y límites:** P09-LOGIN-LIST, P13-DEBUG y P14-NOTFOUND. No se probó una cabecera X-Powered-By en un servidor real. Comparte causa con A10; no contar la misma fuga como dos defectos independientes.

## A03 — Fallos de cadena de suministro

**Estado:** Versiones con avisos confirmadas; explotabilidad de cada CVE pendiente.

**Ruta o componente:** **No corresponde a una URL**: inventario de paquetes de `.venv`, `uv.lock`, `requirements.txt` y construcción Docker.

**Archivo del proyecto:** `uv.lock:364` fija Django 5.2.8; `requirements.txt:46` fija Django 6.0; `Dockerfile:35` instala desde requirements. `Dockerfile:26` copia uv desde latest.

**Qué probé:** Se inventariaron los paquetes realmente instalados y se ejecutó pip-audit sin cambiar las versiones. Se compararon las dos fuentes de resolución y el Dockerfile.

**Qué encontré:** El entorno revisado tiene Django **5.2.8** y el escáner recibió avisos para **17 paquetes**. Hay divergencia entre lock y requirements. Se verificó un aviso oficial de Django corregido en 5.2.9, sin demostrar que Server5K alcance su camino vulnerable.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«Revisé `.venv`, `uv.lock`, `requirements.txt` y `Dockerfile`. Encontré Django 5.2.8 instalado y avisos de seguridad en 17 paquetes mediante pip-audit; además, requirements fija Django 6.0 y el lock fija 5.2.8. Hay dependencias por actualizar y entornos que pueden resolver versiones distintas. No comprobé explotación de cada CVE desde una ruta de la aplicación».

**Evidencia y límites:** HAL-009; `pip-audit.json`, `dependencias-instaladas.txt` y `resumen-dependencias.md`. No llamar “17 vulnerabilidades explotadas”: son 17 paquetes con avisos, incluidos paquetes de desarrollo.

## A04 — Fallos criptográficos

**Estado:** Hash de contraseñas protegido en la prueba; riesgo JWT condicional.

**Ruta o componente:** Contraseñas: método `Juez.set_password()` sin URL propia. JWT: `GET /api/me/`, exclusivamente bajo una configuración de prueba con la clave pública de fallback.

**Archivo del proyecto:** `app/models/juez.py:25` y `:29` usan make_password/check_password. `server/settings.py:13` contiene el fallback; `:210` lo reutiliza para SIGNING_KEY.

**Qué probé:** Se identificó el algoritmo de una contraseña sintética. Por separado se simuló el escenario de usar la constante pública del código como clave JWT y se consultó `/api/me/` con un token firmado con ella.

**Qué encontré:** Se confirmó **pbkdf2_sha256 con sal**, sin MD5 ni contraseña en claro en el modelo. En el escenario de fallback, `/api/me/` devolvió **200**. Esto **no se hizo con el secreto real**: el `.env` local tiene una clave configurada.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«En `app/models/juez.py`, las contraseñas se almacenan usando PBKDF2-SHA256 con sal mediante las funciones de Django: el control de almacenamiento funcionó. Sin embargo, `server/settings.py:13` define una clave pública de respaldo que también firma JWT; al simular ese despliegue, un token firmado con ella accedió a `/api/me/` (200). El riesgo existe si no se configura SECRET_KEY; no se confirmó en la configuración local actual».

**Evidencia y límites:** P04-WEAK-PASSWORD y P17-DEFAULT-SIGNING. La calidad del hash no garantiza contraseñas fuertes: la política débil se registra en A07. TLS público no evaluado.

## A05 — Inyección

**Estado:** Controles efectivos en los flujos probados; sin inyección confirmada.

**Ruta o componente:** `POST /api/login/` y `GET /equipo/6/` (equipo con nombre sintético que contiene un marcador HTML).

**Archivo del proyecto:** `app/views/auth_views.py:69` (consulta ORM), `app/views/html_views.py:151` y `templates/app/equipo_detail.html:32` (`{{ equipo.name }}`).

**Qué probé:** Se envió el texto `' OR 1=1 --` como usuario con contraseña incorrecta. Después se guardó como nombre del equipo un marcador `<script>audit_marker_no_ejecutar</script>` y se revisó el HTML devuelto por la vista.

**Qué encontré:** El login devolvió **401**; no hubo bypass de autenticación. La vista del equipo devolvió **200** y el marcador apareció escapado como `&lt;script&gt;…`, sin etiqueta script sin escapar. Fue una inspección de salida HTML, no una prueba de ejecución en navegador.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«En `POST /api/login/`, el texto SQL de prueba no permitió iniciar sesión y respondió 401; la consulta usa filtros ORM en `app/views/auth_views.py`. En `/equipo/6/`, `templates/app/equipo_detail.html` escapó el marcador HTML del nombre del equipo. No encontré SQLi ni XSS en esos flujos: los controles funcionaron en las pruebas realizadas. No se puede afirmar que toda la aplicación esté libre de inyecciones».

**Evidencia y límites:** P15-SQLI y P16-XSS-ESCAPE. **No marcar “no aplica”**: la categoría sí aplica a una aplicación que procesa entradas; el resultado es “sin hallazgo en lo probado”.

## A06 — Diseño inseguro

**Estado:** Hallazgos de integridad de negocio confirmados.

**Ruta o componente:** `POST /api/equipos/3/registros/` (tiempos negativos) y `POST /api/equipos/5/registros/` (equipo en competencia detenida).

**Archivo del proyecto:** `app/services/registro_service.py:265` (recibe tiempo sin validación de rango); `app/views/registro_views.py:100` y `app/services/registro_service.py:204` (competencia del primer equipo).

**Qué probé:** Caso 1: enviar 15 objetos `{"tiempo": -1000}` para un equipo propio. Caso 2: asignar al mismo juez un primer equipo en competencia activa y otro en una detenida; enviar 15 tiempos al equipo de la detenida.

**Qué encontré:** Ambos casos devolvieron **201** y persistieron 15 registros. El primer caso admite tiempos negativos; el segundo valida una competencia distinta de la del equipo objetivo.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«En `POST /api/equipos/3/registros/` se guardaron 15 tiempos de -1000 ms (201) porque `app/services/registro_service.py` no valida el rango. En `/api/equipos/5/registros/` pude guardar tiempos en una competencia detenida al tener otro equipo en una activa: `registro_views.py:100` y `registro_service.py:204` validan la competencia del primer equipo, no la del solicitado. Son fallos de reglas de negocio e integridad».

**Evidencia y límites:** P05-NEGATIVE y P07-CLOSED-COMPETITION. La recuperación con pregunta secreta de la simulación **no aplica como flujo observado**: Server5K no mostró esa funcionalidad, pero A06 sí aplica a sus reglas de competición.

## A07 — Fallos de autenticación

**Estado:** Hallazgos confirmados en login y política del formulario.

**Ruta o componente:** `POST /api/login/`. Formulario de alta de jueces asociado a `/admin/app/juez/add/`: se probó directamente su clase, no navegando esa URL.

**Archivo del proyecto:** `app/views/auth_views.py:16` (`LoginView`), `server/settings.py:169` (sin throttle configurado) y `app/admin.py:317` (`JuezAdminForm.clean`).

**Qué probé:** Se hicieron seis intentos con contraseña incorrecta de una cuenta sintética y luego uno correcto. Se validó `JuezAdminForm` con password1 y password2 iguales a `123`.

**Qué encontré:** Los fallos respondieron **401** y el siguiente login correcto **200**, sin bloqueo observado. El formulario resultó válido con `123`, aunque la política declarada en settings exige longitud mínima 12: no se invoca esa validación desde el formulario.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«En `POST /api/login/` se permitieron seis intentos fallidos seguidos sin espera ni bloqueo visible; no hay throttle en la vista ni en settings. En `app/admin.py`, `JuezAdminForm.clean` aceptó la contraseña 123 porque sólo verifica obligatoriedad y coincidencia. Se comprobó la clase del formulario que usa `/admin/app/juez/add/`, no un alta administrativa por navegador. Hay fallos de limitación de intentos y aplicación de la política de contraseñas».

**Evidencia y límites:** P03-LOGIN y P04-WEAK-PASSWORD. No se probó un proxy externo y seis intentos no demuestran un umbral ilimitado por sí solos; la revisión del código complementa la prueba.

## A08 — Fallos de integridad de software o datos

**Estado:** Flujos de la simulación no aplicables al módulo revisado; endurecimiento pendiente.

**Ruta o componente:** **No hay URL probada de actualización de software**: no se identificó un actualizador de la aplicación ni un endpoint de deserialización insegura en el alcance revisado.

**Archivo del proyecto:** `Dockerfile:26`: `COPY --from=ghcr.io/astral-sh/uv:latest`. Comparación con `uv.lock`, que sí contiene hashes para paquetes.

**Qué probé:** Se revisó el flujo de instalación y las referencias de herramientas externas del Dockerfile; no se alteró un paquete ni se simuló un ataque a la cadena de distribución.

**Qué encontré:** La herramienta uv se toma de una etiqueta movible sin digest. Es una observación de endurecimiento y reproducibilidad, agrupada con A03/HAL-009. No se demostró sustitución de una descarga, deserialización insegura o ejecución de código alterado.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«No aplica la prueba del instalador o actualizador a un módulo propio identificado en Server5K: no encontré esa funcionalidad dentro del alcance. Tampoco confirmé deserialización insegura. En la construcción sí observé `Dockerfile:26` con uv:latest sin digest, por lo que recomiendo fijar su integridad; esta observación se registra en A03 para no duplicar el mismo hallazgo. La categoría general no se declara completamente segura».

**Evidencia y límites:** Revisión estática de Dockerfile y lock. **No confundir** “no se identificó el flujo de la simulación” con “A08 no puede existir en la aplicación”.

## A09 — Fallos de registro y alerta

**Estado:** Cobertura insuficiente de auditoría de autenticación.

**Ruta o componente:** `POST /api/login/`, observando los eventos de seis fallos de autenticación.

**Archivo del proyecto:** `app/views/auth_views.py:55` (no emite evento estructurado de autenticación); `server/settings.py:279` y `:317` (handlers y nivel raíz).

**Qué probé:** Se capturaron los eventos emitidos durante los intentos fallidos y se revisó el código de login y la configuración de logging.

**Qué encontré:** Se recibieron mensajes genéricos `Unauthorized: /api/login/`, sin identificar al juez intentado ni su origen. No se encontró en esta vista un evento estructurado de éxito/fallo ni una alerta ante repetición. Sí hay otros logs del framework y WebSocket.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«Al probar `POST /api/login/`, los rechazos generaron Unauthorized sin identidad del intento ni origen. En `app/views/auth_views.py` no hay registro estructurado de login exitoso/fallido y en el código revisado no identifiqué alertas por repetición. El problema es cobertura insuficiente de auditoría; no ausencia total de logs. No evalué monitoreo externo».

**Evidencia y límites:** P03-LOGIN y revisión estática. El formato de log incluye fecha; no afirmar que nunca se registra la hora ni que un proxy externo carece de logs.

## A10 — Excepciones y errores mal gestionados

**Estado:** Hallazgos confirmados; algunos errores sí se manejan correctamente.

**Ruta o componente:** `POST /api/login/` con JSON lista; `POST /api/equipos/1/registros/` con `{"registros":15}` o con 15 cadenas; `POST /api/equipos/4/registros/` con lote parcialmente inválido.

**Archivo del proyecto:** `app/views/auth_views.py:59`; `app/views/registro_views.py:74` y `:138`; `app/services/registro_service.py:265`, `:296` y manejo general de excepciones.

**Qué probé:** Se enviaron estructuras JSON de tipo incorrecto. En otro equipo se enviaron 15 elementos: uno con tiempo válido y 14 objetos vacíos; después se reintentó con un lote completo válido.

**Qué encontré:** Login tipo lista y registros como número: **500**. Quince cadenas: **400** con `Error general: 'str' object has no attribute 'get'`. Lote parcial: **201** y un registro guardado; reintento: **400**, porque cualquier registro previo bloquea envíos. Como controles positivos, login sin campos y refresh con tipo incorrecto respondieron 400.

**Texto para pegar en “Hallazgo en mi aplicación”:**

«En `POST /api/login/`, una lista JSON produjo 500 por usar `.get()` sin validar el objeto. En `/api/equipos/1/registros/`, un número en registros produjo 500 y una lista de cadenas expuso un AttributeError en texto. En `/api/equipos/4/registros/`, un lote con 14 errores guardó sólo un tiempo (201) y luego impidió completar el equipo (400). Las causas están en `auth_views.py`, `registro_views.py` y `registro_service.py`. Hay validación incompleta y recuperación inconsistente de errores».

**Evidencia y límites:** P06/P08/P09/P10/P11/P12/P13. Con DEBUG=False los 500 no mostraron traceback; no afirmar una caída sostenida ni que todos los errores filtran detalles.

## Fuentes y evidencias

- [Resultados de las 19 comprobaciones](evidencias/revision-server5k/resultados-pruebas.json).
- [Procedimiento y límites del laboratorio](evidencias/revision-server5k/README.md).
- [Informe con severidad y correcciones](hallazgos-server5k.md).
- [Respuestas a las preguntas de control](README_Practica_OWASP_Top10_2025.md).
- [Lista oficial de categorías](https://top10.owasp.org/2025/).
- [Aviso oficial de Django citado en A03](https://www.djangoproject.com/weblog/2025/dec/02/security-releases/).

# Server5K: qué encontré y cómo comprobarlo

## Empieza aquí

Un **hallazgo** es una diferencia entre lo que la aplicación debería hacer y lo que realmente hizo.
Ejemplo: el juez A debería consultar sólo sus equipos, pero una ruta le devuelve los registros del equipo del juez B.

Preparé un comando que repite las pruebas y las explica en español. Crea sus propios jueces y equipos en una base temporal; **no necesitas crear usuarios, copiar tokens ni encender Server5K**. No utiliza tu base de datos actual. Al terminar elimina los datos de prueba, pero conserva el resultado y los errores controlados en una carpeta `/tmp/server5k-practica-...`.

### 1. Abre una terminal y entra al repositorio de evidencias

```bash
cd /home/joseph/Documentos/Servidor5KAuditar/Server5K-Seguridad
```

### 2. Ejecuta las comprobaciones

```bash
./probar-owasp.sh
```

Espera a que termine. Verás por categoría la ruta, el archivo y el resultado observado. El proceso realiza peticiones internas de prueba: no abre una página ni envía tráfico a `localhost:8000`.

### 3. Para concentrarte en una categoría

```bash
./probar-owasp.sh A01
```

Puedes cambiar A01 por A02, A03, ... A10. **El comando ejecuta siempre las 19 comprobaciones; el argumento selecciona qué explicación muestra.** A03 presenta el escaneo de dependencias ya realizado: no vuelve a consultar CVEs. A08 revisa la referencia de construcción, sin manipular descargas.

Si dice que falta Python, verifica que siga existiendo la instalación en `../Server5K/.venv`. El comando no instala dependencias automáticamente.

## Cómo leer las respuestas

| Código | Significado en esta práctica |
| --- | --- |
| 200 | La consulta fue aceptada y devolvió datos. |
| 201 | La aplicación aceptó el registro. Confirmar también qué se guardó. |
| 400 | Rechazó la entrada. Puede ser el comportamiento correcto. |
| 401 | No aceptó la autenticación. |
| 403 / 404 | Acceso rechazado o recurso no visible para ese usuario. |
| 429 | Se alcanzó un límite de solicitudes. |
| 500 | Ocurrió un error interno; no es una validación adecuada de datos inválidos. |

Un 200 no siempre es bueno: si entrega datos ajenos, demuestra el problema. Un 400 no siempre significa que la prueba falló: puede demostrar que el servidor protegió el recurso.

## A01: el juez puede leer registros ajenos

**En palabras simples:** la aplicación comprueba que iniciaste sesión, pero en una ruta se olvida de comprobar que el equipo sea tuyo.

**Para probar:** `./probar-owasp.sh A01`

El laboratorio hace esto:

1. Crea al juez A y al juez B, cada uno con un equipo.
2. Inicia sesión como A.
3. Pide `GET /api/equipos/2/registros/estado/`, que pertenece a B.
4. Compara con `GET /api/equipos/2/` y con una petición sin token.

**Observado:** estado ajeno 200 con registros; detalle ajeno 404; sin token 401.
**Lo esperado si esa información está restringida al juez:** 403/404 también en la consulta de estado.
**Dónde está:** `app/views/registro_views.py`, clase `EstadoEquipoRegistrosView`, línea 207: busca por ID sin filtrar el juez.
**Qué escribir:** «La ruta de estado devuelve registros de un equipo ajeno al juez autenticado». Considerar que existen resultados públicos al valorar la privacidad.

## A02: el error muestra detalles del servidor

**En palabras simples:** el modo depuración enseña información que sirve al programador, pero que no debería aparecer ante visitantes de producción.

**Para probar:** `./probar-owasp.sh A02`

Se envía `[]` como cuerpo JSON a `POST /api/login/` bajo DEBUG=True. La aplicación esperaba un objeto como `{"username":"...","password":"..."}`.

**Observado:** 500 con traza y ruta del proyecto. Con DEBUG=False, el mismo error fue genérico.
**Dónde está:** `server/settings.py:16` y `app/views/auth_views.py:59`.
**Conclusión:** riesgo si se publica DEBUG=True; no se ha demostrado un servidor de producción expuesto. El 500 por entrada inválida se registra además en A10.

## A03: dependencias con avisos de seguridad

**En palabras simples:** la aplicación puede heredar problemas de una librería que el equipo no escribió.

**Para revisar:** `./probar-owasp.sh A03`

No se prueba entrando a una URL. Se revisan `uv.lock`, `requirements.txt`, los paquetes instalados y `Dockerfile`.

**Observado anteriormente:** Django 5.2.8 instalado y avisos para 17 paquetes. El lock fija Django 5.2.8 y requirements fija 6.0: los entornos pueden instalar versiones diferentes.
**Evidencia:** [resumen del escaneo](evidencias/revision-server5k/resumen-dependencias.md).
**Conclusión:** dependencias por revisar/actualizar; no significa que se hayan explotado 17 vulnerabilidades. Este comando no actualiza el escaneo.

## A04: almacenamiento de contraseñas y clave JWT

**En palabras simples:** una cosa es proteger la contraseña guardada y otra proteger la clave que firma los permisos de acceso.

**Para probar:** `./probar-owasp.sh A04`

- `app/models/juez.py:25`: se comprueba que la contraseña sintética usa PBKDF2-SHA256 con sal. **Este control funcionó**; no se encontró MD5 en ese flujo.
- `server/settings.py:13`: se simula un despliegue que usa la clave pública de respaldo. En ese escenario un token firmado con ella accede a `GET /api/me/` (200).

**Conclusión:** el hash observado es adecuado como mecanismo; el riesgo JWT depende de usar la clave de respaldo. La instalación local tiene una clave configurada. El script nunca imprime ni utiliza su valor.

## A05: SQL y HTML se tratan como datos

**En palabras simples:** se comprueba si un texto introducido se convierte por error en una instrucción.

**Para probar:** `./probar-owasp.sh A05`

1. Envía el texto `' OR 1=1 --` como usuario a `POST /api/login/`.
2. Revisa la salida de `GET /equipo/6/` con un nombre de equipo que contiene un marcador `<script>`.

**Observado:** login 401; marcador HTML escapado como `&lt;script&gt;` en la respuesta.
**Dónde está:** `app/views/auth_views.py` y `templates/app/equipo_detail.html:32`.
**Conclusión para entregar:** «No se encontró SQLi ni XSS en estos casos; los controles funcionaron». **No poner “no aplica”**: la categoría sí aplica, sólo que estas pruebas no encontraron un fallo. No se examinó cada flujo ni ejecución en navegador.

## A06: se aceptan resultados que no deberían existir

**En palabras simples:** la aplicación acepta datos que contradicen las reglas de la carrera.

**Para probar:** `./probar-owasp.sh A06`

**Caso 1 — tiempo negativo:** el laboratorio envía a `POST /api/equipos/3/registros/` una lista de 15 objetos iguales a `{"tiempo":-1000}`.

- Observado: 201 y 15 tiempos negativos guardados.
- Esperado: 400 y ningún registro guardado.
- Archivo: `app/services/registro_service.py:265`.

**Caso 2 — competencia detenida:** crea un juez con un primer equipo en una competencia activa y otro en una detenida; envía tiempos del segundo equipo a `POST /api/equipos/5/registros/`.

- Observado: 201 y 15 registros guardados en la detenida.
- Esperado: rechazar la operación.
- Archivos: `app/views/registro_views.py:100` y `app/services/registro_service.py:204`; ambos miran la competencia del primer equipo, no la del objetivo.

## A07: la aplicación no exige suficiente protección al iniciar sesión

**Para probar:** `./probar-owasp.sh A07`

**Caso 1:** seis intentos incorrectos a `POST /api/login/` y después uno correcto.

- Observado: seis 401 y después 200, sin espera ni bloqueo observado.
- El código tampoco configura throttle. Un límite podría existir en un proxy externo, que no se revisó.

**Caso 2:** probar la clase `JuezAdminForm` de `app/admin.py` con las dos contraseñas iguales a `123`.

- Observado: formulario válido.
- Esperado: error por contraseña demasiado corta.
- Se prueba directamente la clase que usa `/admin/app/juez/add/`; no se afirma haber creado un usuario por navegador.

**Conclusión:** falta aplicar política de contraseñas y limitar intentos en la aplicación revisada.

## A08: no se encontró el actualizador de la simulación

**Para revisar:** `./probar-owasp.sh A08`

No se encontró en el alcance un módulo que descargue e instale actualizaciones como el de la simulación. **Esa prueba específica no aplica al módulo identificado**.

En `Dockerfile:26` sí se observa `uv:latest` sin digest fijo: es una mejora de integridad y reproducibilidad de la construcción, agrupada en A03. No se alteró una descarga ni se demostró ejecución de software manipulado.

## A09: el registro no cuenta toda la historia del login

**En palabras simples:** ver “acceso rechazado” no basta para saber a qué cuenta intentaron entrar y desde dónde.

**Para probar:** `./probar-owasp.sh A09`

El laboratorio captura los mensajes de los seis rechazos de `POST /api/login/`.

**Observado:** `Unauthorized: /api/login/`, sin identidad de la cuenta intentada ni origen en esos eventos.
**Dónde está:** `app/views/auth_views.py` y configuración de logs en `server/settings.py`.
**Conclusión:** existen logs, pero falta contexto de auditoría de autenticación y no se identificaron alertas en el código revisado. La configuración puede registrar hora; no afirmar que no hay ningún registro. Monitoreo externo pendiente.

## A10: una entrada incorrecta causa errores o deja el equipo incompleto

**Para probar:** `./probar-owasp.sh A10`

| Prueba | Resultado observado | Qué debería pasar |
| --- | --- | --- |
| `POST /api/login/` con `[]` | 500 | 400 explicando el formato requerido |
| POST de registros con `{"registros":15}` | 500 | 400 por tipo incorrecto |
| POST de registros con una lista de 15 cadenas | 400 con texto interno AttributeError | 400 con validación comprensible, sin detalle de implementación |
| Lote de 15 elementos: un tiempo válido y 14 objetos vacíos | 201, sólo un tiempo guardado; luego el reenvío válido recibe 400 | Rechazar todo el lote o definir recuperación; no dejarlo bloqueado |

**Dónde está:** `app/views/auth_views.py`, `app/views/registro_views.py` y `app/services/registro_service.py`.
**Conclusión:** validación incompleta y recuperación inconsistente. Algunos errores sí se manejaron bien: login vacío y refresh con tipo incorrecto devolvieron 400.

## Cómo guardar evidencia para la clase

1. Ejecuta una categoría y toma una captura de la terminal con el comando, ruta y resultado visibles.
2. Conserva el JSON de la carpeta `/tmp/server5k-practica-...` que imprime el comando. Copia la evidencia elegida a tu carpeta de evidencias si necesitas conservarla tras reiniciar.
3. En el informe escribe: «Prueba aislada con datos sintéticos mediante cliente interno de Django», sin presentarla como una prueba contra el servidor real.
4. Para el campo de la actividad usa el [registro detallado con texto para pegar](registro-detallado-por-categoria.md).

Los IDs 1–6 pertenecen a la base creada por el script; no uses esos números para asumir que los mismos equipos existen en la base real. Probar manualmente con Postman o curl requeriría preparar las cuentas, sus asignaciones y los tokens correspondientes en un laboratorio separado.

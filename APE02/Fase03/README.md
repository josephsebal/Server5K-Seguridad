## Fase 3: Ataques de inyección: explotación controlada y mitigación de SQLi y XSS

### Sesión 1: Explotación controlada

Las pruebas se dividieron en dos etapas. En la primera (**antes**) se explotaron SQLi y XSS en DVWA, un entorno vulnerable por diseño, para observar el comportamiento de una aplicación sin protección. En la segunda (**después**) se enviaron los mismos tipos de payload a Server5K, donde se verificó que la aplicación ya incorporaba las mitigaciones y no requirió modificaciones. Toda la explotación se realizó en entornos locales y controlados, con payloads mínimos.

## 1. EXPLOTACIÓN CONTROLADA: EL ANTES (DVWA)

Entorno: DVWA local (`http://localhost/dvwa`), nivel de seguridad **Low**.

### 1.1. SQL Injection: prueba con comilla simple

Módulo: *SQL Injection*. Entrada en el campo *User ID*:

```
1'
```

Resultado observado: DVWA devolvió un error de sintaxis SQL generado por el gestor de base de datos.

Análisis: La comilla simple rompió la consulta. Esto confirma que el valor se concatena directamente en la sentencia SQL, sin parametrización. Además, el mensaje de error expone información interna de la base de datos, lo que facilita la explotación.

*Figura 8: Error SQL en DVWA (nivel Low) al ingresar `1'`.*

### 1.2. SQL Injection: prueba de tautología

Entrada en el campo *User ID*:

```
1' OR '1'='1
```

Resultado observado: DVWA devolvió los registros de todos los usuarios de la tabla, no solo el del identificador solicitado.

Análisis: La condición `OR '1'='1'` siempre es verdadera, por lo que la cláusula `WHERE` dejó de filtrar. La entrada alteró la lógica de la consulta, que es el comportamiento característico de una inyección SQL.

*Figura 9: Listado completo de usuarios obtenido en DVWA con la tautología.*

### 1.3. XSS reflejado: prueba de ejecución JavaScript

Módulo: *XSS (Reflected)*. Entrada en el campo *What's your name?*:

```
<script>alert(1)</script>
```

Resultado observado: el navegador ejecutó el script y mostró una ventana de alerta.

Análisis: DVWA incorpora el valor recibido en la página sin codificarlo, por lo que el navegador lo interpretó como código. Un atacante podría usar este mecanismo para robar sesiones o redirigir al usuario.

*Figura 10: Ejecución de `alert(1)` en DVWA mediante XSS reflejado.*

## 2. VERIFICACIÓN DE LA MITIGACIÓN: EL DESPUÉS (SERVER5K)

Los mismos tipos de payload se enviaron a `POST /api/login/` de Server5K desde Swagger UI (`/api/docs/`), con el panel Network de DevTools abierto para registrar la petición y la respuesta. Todas las respuestas fueron HTTP 401, con el mensaje genérico `{"error":"Credenciales inválidas."}`.

### 2.1. SQL Injection: comilla simple

```
POST /api/login/
{ "username": "1'", "password": "x" }
```

Resultado: `HTTP 401 Unauthorized`. A diferencia de DVWA, no hubo error SQL ni información interna. La entrada se trató como un valor de texto.

*Figura 11: Petición con `1'` y respuesta HTTP 401 en Server5K.*

### 2.2. SQL Injection: tautología

```
POST /api/login/
{ "username": "admin' OR '1'='1' #", "password": "x" }
```

Resultado: `HTTP 401 Unauthorized`. La tautología que en DVWA devolvió todos los registros aquí no alteró la consulta ni permitió omitir la autenticación.

*Figura 12: Payload de tautología y respuesta HTTP 401 en Server5K.*

### 2.3. XSS: etiqueta script

```
POST /api/login/
{ "username": "<script>alert(1)</script>", "password": "cualquier_valor" }
```

Resultado: `HTTP 401 Unauthorized`, con un cuerpo JSON fijo que no refleja el valor enviado y sin ventana de alerta. En DVWA el mismo payload se ejecutó.

*Figura 13: Payload con `script` y respuesta HTTP 401 en Server5K.*

## 3. MITIGACIÓN EN CÓDIGO

Al revisar el código se comprobó que ambas protecciones ya estaban implementadas desde el diseño de la aplicación. Por eso no se modificó el proyecto: se documenta el mecanismo que explica los resultados de la sección 2.

### 3.1. Mitigación de SQL Injection: uso del ORM de Django

El inicio de sesión consulta a los usuarios con el ORM de Django, sin construir SQL mediante concatenación de cadenas:

```python
try:
    juez = Juez.objects.filter(
        is_active=True
    ).filter(
        Q(username__iexact=username) | Q(email__iexact=username)
    ).first()
except Exception:
    pass

if juez:
    password_valid = juez.check_password(password)
else:
    check_password(password, 'dummy$pbkdf2-sha256$260000$...')
    password_valid = False
```

*Figura 14: Mitigación de SQL Injection: uso del ORM de Django.*

Análisis: El ORM parametriza internamente las consultas, de modo que los valores del usuario se tratan como datos y no como instrucciones SQL. Esta es la diferencia con DVWA, donde la entrada se concatena en la consulta. La contraseña se verifica con `check_password()`, que compara el valor recibido con el hash almacenado. Si el usuario no existe, se ejecuta igualmente `check_password()` contra un hash ficticio, de modo que el tiempo de respuesta no revela qué cuentas existen. El `try/except` evita que un fallo de consulta exponga detalles internos; se recomienda registrar la excepción con `logger` en lugar de omitirla con `pass`.

Archivo revisado: `app/views/auth_views.py`

### 3.2. Mitigación de XSS: respuesta JSON y escapado automático

La API responde con JSON de contenido fijo, que no incorpora el valor enviado. En las plantillas HTML, Django aplica por defecto el autoescape, que convierte los caracteres especiales en entidades HTML:

```
{{ competencia.name }}
```

Debe evitarse el filtro `safe` con datos no confiables:

```
{# No utilizar con datos no confiables #}
{{ contenido_usuario|safe }}
```

Análisis: El escapado automático hace que los datos dinámicos se muestren como texto y no como HTML o JavaScript. Esto explica que el payload que en DVWA se ejecutó no tuviera efecto en Server5K.

Archivos revisados: `templates/base.html`, `templates/app/competencia_list.html`, `templates/app/competencia_detail.html`

## 4. COMPARATIVA ANTES / DESPUÉS

| Ataque | Payload | DVWA (antes) | Server5K (después) |
|---|---|---|---|
| SQLi: comilla | `1'` | Error SQL expuesto | HTTP 401 genérico |
| SQLi: tautología | `1' OR '1'='1` | Devuelve todos los usuarios | HTTP 401, sin acceso |
| XSS reflejado | `<script>alert(1)</script>` | Se ejecuta la alerta | HTTP 401, JSON sin reflejar el valor |
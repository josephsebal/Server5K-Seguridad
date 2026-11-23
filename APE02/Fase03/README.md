# Fase 3: Ataques de inyección: explotación controlada y mitigación de SQLi y XSS

**Proyecto:** Server5K (Django 6.0 + Django REST Framework, PostgreSQL con Docker Compose)
**Entorno:** solo `localhost` (`http://localhost:8000`), con datos ficticios de laboratorio.

## Sesión 1: Explotación controlada

## 1. EXPLOTACIÓN CONTROLADA: EL ANTES

> **Aclaración:** Server5K no tiene endpoints vulnerables a SQLi ni a XSS, así que las pruebas 1.1 a 1.3 muestran la protección ya vigente. El estado vulnerable real se demuestra en DVWA (apartado 1.4), como permite la guía.

### 1.1. SQL Injection: prueba con comilla simple

**Petición probada:**
```http
POST /api/login/
Content-Type: application/json

{
    "username": "1'",
    "password": "x"
}
```
**Resultado observado:**
```
HTTP 401 Unauthorized
{"error":"Credenciales inválidas."}
```
**Análisis:**
La entrada que contiene una comilla simple no produjo un error SQL ni permitió realizar una autenticación exitosa. El servidor respondió con un código HTTP 401, indicando que las credenciales proporcionadas no fueron aceptadas.

[INSERTAR CAPTURA: evidencias/04_sqli_comilla_login_401.png]
*Figura 1: Captura de pantalla de la petición con el valor `1'` y la respuesta HTTP 401.*

### 1.2. SQL Injection: prueba de tautología

**Petición probada:**
```http
POST /api/login/
Content-Type: application/json

{
    "username": "admin' OR '1'='1' #",
    "password": "x"
}
```
**Resultado observado:**
```
HTTP 401 Unauthorized
{"error":"Credenciales inválidas."}
```
**Análisis:**
Se utilizó una expresión lógica de tautología para comprobar si era posible alterar la condición de autenticación. Sin embargo, la aplicación rechazó la petición y devolvió el código HTTP 401. No se consiguió omitir el proceso de autenticación ni acceder al sistema mediante la entrada proporcionada.

[INSERTAR CAPTURA: evidencias/05_sqli_tautologia_login_401.png]
*Figura 2: Captura de pantalla del payload de tautología y la respuesta HTTP 401.*

### 1.3. Payload `<script>` en el login

**Petición probada:**
```http
POST /api/login/
Content-Type: application/json

{
    "username": "<script>alert(1)</script>",
    "password": "cualquier_valor"
}
```
**Resultado observado:**
```
HTTP 401 Unauthorized
Content-Type: application/json
{"error":"Credenciales inválidas."}
```
**Análisis:**
Se envió una etiqueta script como valor del campo `username` para comprobar si la aplicación la devolvía como contenido ejecutable. La respuesta fue HTTP 401 en JSON, un formato que el navegador no interpreta como HTML, y no se observó ninguna ventana de alerta. Como el login devuelve JSON, este caso solo demuestra que la API no refleja el payload. La prueba de XSS sobre una página HTML está en el apartado 3.

[INSERTAR CAPTURA: evidencias/06_xss_script_login_401.png]
*Figura 3: Captura de pantalla del payload enviado y la respuesta HTTP 401.*

### 1.4. Explotación en DVWA (estado vulnerable)

Pendiente de capturar en DVWA local, con nivel de seguridad **Low** (`docker run --rm -d -p 8081:80 --name dvwa vulnerables/web-dvwa`):

| Prueba | Módulo | Payload | Resultado esperado | Captura |
|---|---|---|---|---|
| SQLi comilla simple | SQL Injection | `'` | Error SQL | [INSERTAR CAPTURA: evidencias/01_sqli_comilla_dvwa.png] |
| SQLi tautología | SQL Injection | `' OR '1'='1` | Lista de todos los usuarios | [INSERTAR CAPTURA: evidencias/02_sqli_tautologia_dvwa.png] |
| XSS reflejado | XSS (Reflected) | `<script>alert(1)</script>` | Se ejecuta `alert(1)` | [INSERTAR CAPTURA: evidencias/03_xss_reflejado_dvwa.png] |

## 2. MITIGACIÓN EN CÓDIGO

### 2.1. Mitigación de SQL Injection: utilización del ORM de Django

En el proceso de inicio de sesión se utiliza el ORM (Object-Relational Mapping) de Django para consultar los registros de usuarios, evitando construir consultas SQL mediante concatenación directa de cadenas.

El fragmento de código utilizado es el siguiente (`Server5K/app/views/auth_views.py`):
```python
juez = Juez.objects.filter(
    is_active=True
).filter(
    Q(username__iexact=username) | Q(email__iexact=username)
).first()

if juez:
    password_valid = juez.check_password(password)
else:
    check_password(password, 'dummy$pbkdf2-sha256$260000$...')  # iguala el tiempo de respuesta
    password_valid = False
```
[INSERTAR CAPTURA: evidencias/10_codigo_orm.png]
*Figura 4: Mitigación de SQL Injection: utilización del ORM de Django.*

**Análisis de la mitigación:**
El ORM envía la consulta y los valores por separado (`WHERE ... LIKE %s`), por lo que los valores del usuario no se interpretan como instrucciones SQL. Además, la contraseña no llega a la base de datos: se verifica con `check_password()`, que compara el valor recibido con el hash almacenado. El `else` ejecuta una comprobación ficticia para que usuarios existentes e inexistentes tarden lo mismo.
Complementos: el proyecto no usa `.raw()`, `.extra()` ni `cursor.execute()`. Los filtros por URL (`?categoria=`, `?competition_id=`, `?judge_id=`) pasan por `filter()`, las rutas usan `<int:pk>`, y `serializers.py` valida tipo y longitud (`IntegerField`, `max_length=15`, tiempos no negativos).

**Archivo revisado:** `app/views/auth_views.py`

### 2.2. Mitigación de XSS: escapado automático de salida

Django dispone de un mecanismo de autoescape habilitado por defecto en sus plantillas, el cual permite convertir caracteres especiales en entidades HTML para evitar que el contenido dinámico sea interpretado como código ejecutable.

Ejemplo de utilización segura:
```django
{{ competencia.name }}
```
Se debe evitar el uso del filtro `safe` cuando se trabaja con contenido que proviene de entradas no confiables.

Ejemplo de utilización insegura (no usado en el proyecto):
```django
{# No utilizar con datos no confiables #}
{{ contenido_usuario|safe }}
```
**Análisis de la mitigación:**
El escapado automático permite que los datos dinámicos se presenten como texto y no como instrucciones HTML o JavaScript. En el proyecto no hay `|safe`, `mark_safe` ni `{% autoescape off %}`, `admin.py` usa `format_html` y el parámetro `?categoria=` nunca se imprime tal cual. Cabeceras activas: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`.

**Archivos revisados:**
- `templates/base.html`
- `templates/app/competencia_list.html`
- `templates/app/competencia_detail.html`
- `templates/app/partials/competencia_results.html`

**Limitación:** la aplicación **no envía** `Content-Security-Policy` (ver `evidencias/08_xss_html_cabeceras.txt`). Sería una defensa en profundidad recomendable, por ejemplo `default-src 'self'; script-src 'self'; object-src 'none'`, pero no se implementó en esta fase y requiere revisar antes los scripts inline y los usos de `innerHTML` de `competencia_detail.html`.

## 3. VERIFICACIÓN / RE-TEST (DESPUÉS)

Se repitieron los payloads contra la aplicación en ejecución.

| # | Endpoint | Payload | Resultado | Evidencia |
|---|---|---|---|---|
| 1 | `POST /api/login/` | `1'` | 401, sin error SQL | `04_sqli_comilla_login_401.png` |
| 2 | `POST /api/login/` | `admin' OR '1'='1' #` | 401, sin bypass | `05_sqli_tautologia_login_401.png` |
| 3 | `POST /api/login/` | `' OR '1'='1' -- ` | 401, sin bypass | `curl` |
| 4 | `POST /api/login/` | `<script>alert(1)</script>` | 401, respuesta JSON | `06_xss_script_login_401.png` |
| 5 | `GET /5/?categoria=<script>alert(1)</script>` | `<script>alert(1)</script>` | 200, el nombre se muestra como texto y no hay pop-up | `07_xss_html_escapado_despues.png` |
| 6 | Mismo GET | HTML devuelto | `&lt;script&gt;alert(1)&lt;/script&gt;` en `<title>`, breadcrumb y encabezado | `08_xss_html_cabeceras.txt` |
| 7 | `POST /api/login/` | Credenciales válidas de laboratorio | 200 (control positivo) | `curl` |

Para la prueba 5 se creó en la base local una competencia llamada `LAB-F3 <script>alert(1)</script>` con un equipo `<script>alert(1)</script>`, que se muestran escapados.

[INSERTAR CAPTURA: evidencias/07_xss_html_escapado_despues.png]
*Figura 5: Página de detalle mostrando el script como texto, sin ejecución.*

Reproducción sin navegador:
```bash
curl -i -H "Content-Type: application/json" -d '{"username":"1'"'"'","password":"x"}' http://localhost:8000/api/login/
curl -i "http://localhost:8000/5/?categoria=%3Cscript%3Ealert(1)%3C/script%3E"
```

## 4. CONCLUSIONES

- Server5K resiste los payloads de SQLi y XSS probados porque el ORM parametriza las consultas y las plantillas escapan la salida, no por casualidad.
- La explotación real se demuestra en DVWA, un entorno diseñado para ello.
- Mejora pendiente: agregar `Content-Security-Policy` como defensa en profundidad.
- Todas las pruebas se hicieron en `localhost` con datos ficticios.

### Pregunta de Control Nro. 3
**¿Por qué la validación de entrada por sí sola no basta contra SQLi y XSS?**
La validación decide qué entradas se aceptan, pero no cambia cómo se usan después. Un nombre de equipo legítimo puede contener `'` o `<`, como `O'Brien <Norte>`, y rechazarlo no es una solución general. Si el dato se concatenara en SQL o se imprimiera sin escapar, una entrada que pase la validación seguiría siendo peligrosa. En Server5K el login acepta cualquier texto como `username`, pero el ORM lo envía como parámetro y no como SQL, y los nombres de competencia y equipos se muestran escapados (`&lt;script&gt;`). Por eso las defensas principales son la consulta parametrizada y el escapado de salida según el contexto, con la CSP como refuerzo. La validación es solo una capa más.

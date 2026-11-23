# APE 02 – Fase 3: Ataques de inyección (SQLi y XSS)

**Proyecto:** Server5K (Django 6.0 + Django REST Framework, PostgreSQL vía Docker Compose)
**Entorno:** solo `localhost` (`http://localhost:8000`), con datos ficticios de laboratorio.
**Ciclo:** Hallazgo → Mitigación → Verificación.

## Hallazgo principal

La revisión del código y las pruebas muestran que Server5K **no presenta SQLi ni XSS reflejado explotables**. Las defensas existen por diseño del framework (ORM parametrizado y autoescape de plantillas). Por eso las pruebas sobre la aplicación son evidencia de la protección **ya vigente**. No son un "antes vulnerable". El "antes" vulnerable corresponde a DVWA, como permite la guía (sección 1.4).

---

## 1. Explotación controlada (Antes)

### 1.1 SQL Injection: comilla simple
```
POST /api/login/
Content-Type: application/json

{"username": "1'", "password": "x"}
```
**Resultado:** `HTTP 401` `{"error":"Credenciales inválidas."}`. No hay error SQL ni acceso.

[INSERTAR CAPTURA: evidencias/04_sqli_comilla_login_401.png]

### 1.2 SQL Injection: tautología
```
{"username": "admin' OR '1'='1' #", "password": "x"}
```
**Resultado:** `HTTP 401`. La tautología no altera la condición de autenticación.

[INSERTAR CAPTURA: evidencias/05_sqli_tautologia_login_401.png]

### 1.3 Payload `<script>` en el login
```
{"username": "<script>alert(1)</script>", "password": "cualquier_valor"}
```
**Resultado:** `HTTP 401` con `Content-Type: application/json`. Una respuesta JSON no se interpreta como HTML, así que este caso solo muestra que la API no refleja el payload. La prueba de XSS reflejado sobre HTML está en la sección 3.

[INSERTAR CAPTURA: evidencias/06_xss_script_login_401.png]

### 1.4 Explotación en DVWA (estado vulnerable real)
Pendiente de capturar, con DVWA local en nivel de seguridad **Low** (`docker run --rm -d -p 8081:80 --name dvwa vulnerables/web-dvwa`):

| Prueba | Módulo | Payload | Resultado esperado | Captura |
|---|---|---|---|---|
| SQLi comilla | SQL Injection | `'` | Error SQL de MySQL | [INSERTAR CAPTURA: evidencias/01_sqli_comilla_dvwa.png] |
| SQLi tautología | SQL Injection | `' OR '1'='1` | Lista de todos los usuarios | [INSERTAR CAPTURA: evidencias/02_sqli_tautologia_dvwa.png] |
| XSS reflejado | XSS (Reflected) | `<script>alert(1)</script>` | Pop-up `alert(1)` | [INSERTAR CAPTURA: evidencias/03_xss_reflejado_dvwa.png] |

> Nota: los payloads `' OR '1'='1' #` y `-- ` se probaron solo contra Server5K, donde dan 401 (`evidencias/08`).

---

## 2. Mitigación en código

### 2.1 SQLi: consultas parametrizadas mediante el ORM de Django
Archivo: `Server5K/app/views/auth_views.py` (login, líneas 59-90).

```python
juez = Juez.objects.filter(
    is_active=True
).filter(
    Q(username__iexact=username) | Q(email__iexact=username)
).first()

if juez:
    password_valid = juez.check_password(password)
else:
    check_password(password, 'dummy$pbkdf2-sha256$260000$...')  # igualar tiempos
    password_valid = False
```
- El ORM envía la consulta y los valores por separado (`WHERE ... LIKE %s`), así que una comilla o `' OR '1'='1` es texto de búsqueda y no cambia la estructura del SQL.
- La contraseña nunca viaja a la base de datos: se compara con `check_password()` contra el hash.
- El `else` ejecuta un `check_password` ficticio para que usuarios existentes e inexistentes tarden igual.
- No hay `.raw()`, `.extra()`, `cursor.execute()` ni `RawSQL` en el proyecto.
- Filtros por URL (`?categoria=`, `?competition_id=`, `?judge_id=`) usan `filter()` y las rutas usan `<int:pk>`.
- Validación de entrada: `serializers.py` (`IntegerField`, `max_length=15`, rechazo de tiempos negativos).

### 2.2 XSS: escapado automático de salida
- Las plantillas de Django escapan `<`, `>`, `&`, `"` y `'` en cada `{{ variable }}`, por ejemplo `{{ competencia.name }}` en `competencia_detail.html` y `{{ equipo.name }}` en `partials/competencia_results.html`.
- El proyecto no usa `|safe`, `mark_safe` ni `{% autoescape off %}`.
- El parámetro `?categoria=` solo se usa como condición y nunca se imprime tal cual.
- `admin.py` usa `format_html`, que también escapa.
- Cabeceras activas: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`.

### 2.3 Limitación: no hay Content-Security-Policy
La aplicación **no envía** `Content-Security-Policy` (comprobado en `evidencias/08_xss_html_cabeceras.txt`). La CSP sería una capa adicional por si algún día un campo se imprime sin escapar. Propuesta (no implementada en esta fase):
`Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'`.
Hay que revisar antes los scripts inline de las plantillas y los usos de `innerHTML` en `competencia_detail.html`.

---

## 3. Verificación / Re-test (Después)

Se repitieron los payloads contra la aplicación en ejecución.

| # | Endpoint | Payload | Resultado | Evidencia |
|---|---|---|---|---|
| 1 | `POST /api/login/` | `1'` | 401, sin error SQL | `04_sqli_comilla_login_401.png` |
| 2 | `POST /api/login/` | `admin' OR '1'='1' #` | 401, sin bypass | `05_sqli_tautologia_login_401.png` |
| 3 | `POST /api/login/` | `' OR '1'='1' -- ` | 401, sin bypass | repetido con `curl` |
| 4 | `POST /api/login/` | `<script>alert(1)</script>` | 401, respuesta JSON | `06_xss_script_login_401.png` |
| 5 | `GET /5/?categoria=<script>alert(1)</script>` | `<script>alert(1)</script>` | 200, el nombre se muestra como texto y no hay pop-up | `07_xss_html_escapado_despues.png` |
| 6 | Mismo GET | Código fuente de la página | `&lt;script&gt;alert(1)&lt;/script&gt;` en `<title>`, breadcrumb y encabezado | `08_xss_html_cabeceras.txt` |
| 7 | `POST /api/login/` | Credenciales válidas de laboratorio | 200 (control positivo: el filtro no rompe el login legítimo) | `curl` |

Para el caso 5 se creó, en la base local de laboratorio, una competencia con el nombre `LAB-F3 <script>alert(1)</script>` y un equipo `<script>alert(1)</script>`, que se muestran como texto.

[INSERTAR CAPTURA: evidencias/07_xss_html_escapado_despues.png]

Reproducción sin navegador:
```
curl -i -H "Content-Type: application/json" -d '{"username":"1'"'"'","password":"x"}' http://localhost:8000/api/login/
curl -i "http://localhost:8000/5/?categoria=%3Cscript%3Ealert(1)%3C/script%3E"
```

**Observación sobre las capturas.** Si el panel *Payload* de DevTools muestra una petición anterior con el JSON mal formado (por ejemplo `""admin'...`), esa fila es un intento previo con respuesta 400 (`JSON parse error`), no el 401 válido. Antes de entregar, conviene tomar la captura con la fila correcta seleccionada.

---

## 4. Conclusiones
- Server5K resiste los payloads de SQLi y XSS probados: el ORM parametriza todas las consultas y las plantillas escapan la salida.
- El ataque no fracasó por casualidad, sino porque **no hay concatenación de SQL ni salida sin escapar** en el código revisado.
- Falta la CSP como defensa en profundidad, y conviene vigilar el uso de `innerHTML` en `competencia_detail.html`.
- El "antes" explotable se demuestra en DVWA, un entorno diseñado para eso.
- Todas las pruebas se hicieron en `localhost` con datos ficticios.

### Pregunta de Control Nro. 3
**¿Por qué la validación de entrada por sí sola no basta contra SQLi y XSS?**
La validación decide qué entradas se aceptan, pero no cambia cómo se usan después. Un nombre de equipo legítimo puede contener `'` o `<`, como `O'Brien <Norte>`, y rechazarlo no es una solución general. Si el dato se concatenara en SQL o se imprimiera sin escapar, una entrada que pase la validación seguiría siendo peligrosa. En Server5K el login recibe cualquier texto como `username`, pero el ORM lo envía como parámetro y no como SQL. Los nombres de competencia y equipos se muestran escapados (`&lt;script&gt;`). Las defensas son la consulta parametrizada, el escapado de salida según el contexto y, como refuerzo, la CSP. La validación es una capa más, no la defensa principal.

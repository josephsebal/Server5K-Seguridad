# APE 02 · Fase 1 · Criptografía aplicada

El reporte APE 02 aportado describe una revisión local de Server5K, commit `826aec5c`, con SQLite y cuentas ficticias. El modelo `Juez` emplea `make_password()` y `check_password()` de Django. En la prueba se observó un hash con prefijo `pbkdf2_sha256$1200000$`; dos hashes de una misma contraseña de laboratorio resultaron distintos por sus sales individuales. No se publican contraseñas ni hashes completos.

| Hallazgo | Riesgo y tratamiento propuesto |
| --- | --- |
| `SECRET_KEY` con valor de respaldo conocido | Si falta la variable de entorno en producción, también se debilita la firma JWT HS256. Impedir el arranque sin una clave privada fuerte y usar claves distintas por entorno. No se verificó que esto ocurra en producción. |
| Credenciales de demostración | Los comandos de carga pueden usar claves previsibles o escribirlas en archivos. Generar credenciales de prueba aleatorias, restringir esos archivos y no incluirlos en el repositorio. |
| HTTPS condicionado | La configuración local con `ENABLE_HTTPS=False` desactiva redirección y marcas Secure; PostgreSQL de ejemplo usa `sslmode=disable`. Comprobar TLS, HTTPS/WSS y cifrado hacia PostgreSQL en el despliegue real. |

La mejora propuesta es introducir Argon2id como primer hasher, conservar PBKDF2 temporalmente para migrar las contraseñas al autenticarse y gestionar claves y credenciales fuera del repositorio. **La migración no consta como ejecutada en este portafolio.** Estas conclusiones pertenecen a la versión del código citada por el reporte; no se extrapolan automáticamente a commits posteriores.

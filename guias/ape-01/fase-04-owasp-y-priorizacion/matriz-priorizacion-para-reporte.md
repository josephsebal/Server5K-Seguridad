# Actividad 1: Matriz de priorización

Proyecto: Server5K. Fecha de elaboración: 23 de octubre de 2026.

## Criterio utilizado

Se integraron el inventario de rutas de la fase 1, la valoración de activos CIA de la fase 2, los errores revisados en la fase 3 y la lista OWASP de la fase 4. No se añadió un hallazgo por fase de manera artificial: una ruta expuesta o una amenaza del inventario no constituyen por sí mismas una vulnerabilidad.

La escala es una propuesta de trabajo para este reporte, no una escala exigida por la guía ni una valoración CVSS.

| Valor | Impacto: cuánto daño puede causar | Probabilidad: condiciones para que ocurra |
| --- | --- | --- |
| 1 — Bajo | Efecto menor, sin comprometer una función importante. | Requiere una condición no confirmada en el entorno o un uso vulnerable aún no demostrado. |
| 2 — Medio | Expone información operativa, dificulta investigar o afecta una función de forma recuperable. | Requiere una cuenta, una entrada preparada u otras condiciones concretas reproducidas. |
| 3 — Alto | Puede alterar resultados de la carrera o permitir actuar como otra persona. | El escenario afectado está confirmado y la acción está directamente disponible sin barreras significativas. |

**Riesgo = impacto × probabilidad.** Bajo: 1–2; medio: 3–4; alto: 6–9.

Los valores de probabilidad son estimaciones cualitativas, no porcentajes. Un riesgo condicionado o de alcance pendiente permanece identificado como tal aunque tenga puntuación. La selección final también considera la evidencia y la relación con la función principal de Server5K.

## Matriz de impacto y probabilidad

| ID del reporte | Categoría | Hallazgo o riesgo identificado | Estado de la evidencia | Impacto | Probabilidad | Resultado | Nivel | Justificación y acción recomendada |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M-01 | A06 — Diseño inseguro | Se guardan tiempos negativos en POST /api/equipos/3/registros/. | Confirmado en laboratorio, incluido Swagger. HAL-004. | 3 | 2 | 6 | Alto | Un juez asignado puede introducir resultados inválidos y afectar la clasificación de la carrera. Validar los 15 tiempos antes de guardar y rechazar el lote si alguno es inválido. |
| M-02 | A07 — Autenticación | No hay limitación de intentos en el código revisado y el formulario de jueces acepta contraseñas débiles. | Código y pruebas acotadas: seis rechazos sin bloqueo; formulario válido con 123. HAL-002/HAL-003. | 3 | 2 | 6 | Alto | Facilita intentar adivinar credenciales; si se acierta, permite actuar como juez. No se demostró toma de una cuenta real. Aplicar límites por cuenta/IP y validar contraseñas al crearlas o cambiarlas. |
| M-03 | A01 — Control de acceso | Un juez puede leer registros de un equipo de otro juez en GET /api/equipos/2/registros/estado/. | Confirmado con dos jueces ficticios. HAL-001. | 2 | 2 | 4 | Medio | Rompe el aislamiento de esa API entre jueces. El impacto se modera porque parte de los resultados es pública y no se demostró escritura ajena. Comprobar pertenencia o permiso explícito del objeto. |
| M-04 | A10 — Manejo de errores | Entradas JSON incorrectas provocan 500 o devuelven detalles internos de excepciones. | Confirmado en pruebas de tipos incorrectos. HAL-007. | 2 | 2 | 4 | Medio | Revela detalles de implementación y maneja mal entradas inválidas; no se probó caída sostenida del servicio. Validar estructuras y mostrar mensajes comprensibles sin excepciones internas. |
| M-05 | A09 — Registro y alertas | El rechazo de login no incluye cuenta intentada ni origen en el log observado. | Observado en el log y complementado con revisión de la vista. HAL-010. | 2 | 2 | 4 | Medio | Dificulta reconocer e investigar intentos sospechosos. Registrar eventos de autenticación con contexto y definir alertas, sin guardar contraseñas o tokens. No se evaluó monitoreo externo. |
| M-06 | A03 — Cadena de suministro | Hay paquetes instalados con avisos de seguridad y versiones distintas entre uv.lock y requirements.txt. | Escaneo de paquetes y revisión de archivos; alcance de cada CVE pendiente. HAL-009. | 3 | 1 | 3 | Medio, potencial | Una dependencia vulnerable podría afectar funciones importantes, pero no se demostró un camino explotable en Server5K. Revisar avisos aplicables, unificar versiones, actualizar y repetir pruebas. |
| M-07 | A04 — Criptografía | Si falta SECRET_KEY, el código puede usar una clave pública de respaldo para firmar JWT. | Configuración simulada confirmada; no se comprobó esa condición en el .env local actual. HAL-008. | 3 | 1 | 3 | Medio en la valoración actual; condicionado | Si un despliegue usa esa clave conocida, permitiría crear tokens falsos. Exigir una clave segura al iniciar y verificar la configuración de cada entorno. Si se confirma el uso del respaldo, pasa a atención inmediata. |
| M-08 | A02 — Configuración | DEBUG=True muestra trazas y rutas ante ciertos errores. | Reproducido con modo desarrollo; producción expuesta no confirmada. Vinculado a HAL-007. | 2 | 1 | 2 | Bajo en laboratorio; condicionado | El detalle técnico sería visible si se publica ese modo. Mantener DEBUG=False en producción y comprobar HTTPS y cookies en el despliegue real. Se relaciona con M-04 y no debe contarse como una segunda fuga independiente. |

Los identificadores de equipo corresponden al laboratorio temporal y pueden cambiar en la instalación real. La matriz resume el reporte académico; los IDs M-01–M-08 se enlazan con los HAL ya existentes, sin renumerarlos.

## Tres hallazgos seleccionados

### 1. Tiempos negativos aceptados — M-01 / A06

Se seleccionó porque afecta directamente el dato principal del sistema: los tiempos de la carrera. La evidencia en Swagger muestra respuesta 201 y 15 tiempos de -1000 aceptados. Un resultado inválido puede alterar la clasificación y la confianza en la competencia.

**Primera corrección propuesta:** validar el lote completo y guardar los registros sólo cuando todos sean válidos.

### 2. Autenticación insuficientemente protegida — M-02 / A07

Se seleccionó porque el acceso de un juez habilita funciones sensibles. El código no aplica limitación de intentos y el formulario admite una contraseña corta. Se confirmó la debilidad del control, no una toma de cuenta mediante fuerza bruta. Un proxy externo podría añadir límites y no fue evaluado.

**Primera corrección propuesta:** aplicar límites por cuenta/IP y ejecutar la política de contraseñas en el formulario de jueces.

### 3. Lectura de registros de equipos ajenos — M-03 / A01

Se seleccionó porque se demostró con dos identidades distintas: el estado del equipo ajeno respondió 200 mientras el detalle del mismo equipo respondió 404. Evidencia una comprobación de permisos inconsistente y permite abordar control de acceso en APE 02. La valoración no presupone que todos los tiempos sean privados.

**Primera corrección propuesta:** recuperar el equipo filtrando por el juez autenticado o verificar un permiso de objeto explícito.

M-03 se prioriza sobre otros riesgos medios porque la diferencia de autorización está reproducida y afecta el límite entre usuarios. Los avisos de dependencias y la clave de respaldo requieren confirmar condiciones del despliegue. La prioridad debe revisarse si aparece evidencia de mayor exposición.

## Resultados que no se registran como vulnerabilidades confirmadas

- **A05:** el intento SQL fue rechazado y el marcador HTML quedó escapado en los flujos probados. Mantener estos controles y ampliar la cobertura; no significa que toda la aplicación esté certificada como segura.
- **A08:** no se demostró aceptación de software alterado. La referencia uv:latest se conserva como observación de construcción dentro de A03, no como un hallazgo A08 independiente.
- La duración de los tokens por sí sola no demuestra una vulnerabilidad: depende de los requisitos de sesión, revocación y exposición.
- HTTP local y DEBUG de laboratorio no demuestran una vulnerabilidad desplegada en producción.

## Evidencias utilizadas y precisiones del reporte

- [Resultados de pruebas aisladas](evidencias/revision-server5k/resultados-pruebas.json): P01, P03, P04, P05, P09, P10, P11, P13, P15, P16 y P17.
- [Captura de Swagger A06](evidencias/revision-server5k/EVI-A06-swagger-tiempo-negativo.jpg).
- [Log de rechazo A09](evidencias/revision-server5k/EVI-A09-log-login-rechazado.txt) y [captura de la solicitud](evidencias/revision-server5k/EVI-A09-swagger-login-rechazado.jpg).
- [Escaneo de paquetes instalados](evidencias/revision-server5k/pip-audit.json) y [resumen](evidencias/revision-server5k/resumen-dependencias.md).
- [Informe técnico y referencias de código](hallazgos-server5k.md).

La copia del reporte menciona 201 vulnerabilidades, un escaneo de requirements.txt y 19 advertencias de check --deploy. Las evidencias disponibles aquí corresponden al inventario de paquetes instalados y contienen avisos repetidos; no se usa 201 como número verificado de vulnerabilidades únicas o explotables. Tampoco se utiliza el número de advertencias de check --deploy como prueba sin su salida. La clave secreta real no se incluye ni se afirma débil a partir de su sola presencia en .env.

El borrador de reporte declara Django 6.0 según requirements.txt; las pruebas documentadas se ejecutaron con Django 5.2.8 instalado. Esta diferencia se conserva en M-06 para distinguir los entornos.

## Párrafo para incorporar al informe

A partir del inventario de superficie de ataque, la valoración de activos según la tríada CIA, las pruebas de errores y la lista OWASP, se construyó una matriz de impacto y probabilidad con una escala de uno a tres. Se priorizaron la aceptación de tiempos negativos, la protección insuficiente de la autenticación y la consulta de registros de equipos ajenos, debido a su evidencia y a su efecto sobre los resultados de la carrera y el acceso de los jueces. Los riesgos que dependen de una configuración o de un uso vulnerable aún no demostrado se registraron de forma condicionada. Esta matriz orienta las correcciones y verificaciones de la guía APE 02.

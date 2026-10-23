# Informe consolidado — APE 01

## Datos generales

- **Proyecto:** Server5K — Sistema de competencias 5K.
- **Integrantes:** Darwin Enrique Granda Orosco, Darwin Andrés Sarango Soto y Joseph Sebastian Balcazar Loaiza.
- **Asignatura / ciclo / unidad:** Software Security / 8A / Unidad 1.
- **Docente:** Valeria Herrera Salazar.
- **Período académico de la práctica:** 28 de septiembre a 23 de octubre de 2026.
- **Objetivo:** construir la línea base de seguridad mediante alcance, superficie de ataque, valoración CIA, revisión de errores y mapeo OWASP.

## Documento fuente

[Reporte completo, copia preparada para publicación](../../entregas/APE-01-reporte-publicacion.pdf). Se conservaron las 16 páginas y el texto; cinco capturas sensibles se retiraron de la copia pública. [Detalle de la preparación](../../entregas/README.md).

## Desarrollo por fase

### Fase 1 — Aplicación y superficie de ataque

Se seleccionó una aplicación con código disponible, autenticación, base de datos, API REST y WebSocket. Se definieron módulos dentro y fuera del alcance y se registraron 16 elementos expuestos. Se incorporan cuatro figuras de los autores: repositorio, servicios, interfaz y Swagger.

[Ficha](fase-01-seleccion-y-superficie/ficha-proyecto.md) · [Inventario](fase-01-seleccion-y-superficie/inventario-superficie.md).

### Fase 2 — Tríada CIA

Se clasificaron 12 activos en confidencialidad, integridad y disponibilidad, con amenazas y dos controles propuestos para cada uno. Se destaca la integridad de los tiempos/resultados y la confidencialidad de credenciales y secretos. Se diferencia clasificación de activos de evidencia de vulnerabilidades.

[Matriz CIA](fase-02-activos-y-amenazas/matriz-activos-amenazas.md) · [Controles](fase-02-activos-y-amenazas/controles-mitigacion.md).

### Fase 3 — Errores y fugas

Se documentan pruebas de entradas incorrectas, respuestas 400/500, exposición de detalles de implementación y trazas condicionadas al modo DEBUG. Se proponen validación de entrada, mensajes de error adecuados, logs restringidos y consistencia transaccional. No se presentan propuestas como correcciones implementadas.

[Informe de fase](fase-03-gestion-de-errores/informe-fase.md) · [Registro](fase-03-gestion-de-errores/registro-errores.md).

### Fase 4 — OWASP y matriz de riesgo

La lista de diez categorías distingue hallazgos confirmados, controles que funcionaron y escenarios no demostrados. Se priorizan: tiempos negativos (A06), autenticación insuficientemente protegida (A07) y consulta de registros ajenos (A01).

[Lista OWASP](fase-04-owasp-y-priorizacion/lista-cotejo-owasp.md) · [Matriz y selección](fase-04-owasp-y-priorizacion/matriz-priorizacion-para-reporte.md).

## Conclusiones y continuidad

Server5K proporciona un caso con varias superficies de exposición. La línea base documenta activos, permisos, entradas y riesgos para orientar la auditoría técnica de APE 02. Las correcciones deben validar tiempos, aplicar permisos por objeto y fortalecer autenticación; también deben mejorarse registros y revisarse dependencias y configuración de cada despliegue.

El trabajo no certifica seguridad global ni explotación productiva de cada riesgo. Las pruebas internas usan SQLite temporal y Channels en memoria; las capturas de Docker provienen del documento. Se conserva la diferencia entre Django 6.0 declarado y 5.2.8 probado, así como el análisis pendiente de alcance de los avisos CVE.

[Insumo para APE 02](fase-04-owasp-y-priorizacion/insumo-ape-02.md) · [Preguntas de control](preguntas-de-control.md).

# Informe de fase 4 — OWASP y priorización

Fuente: [Reporte de los integrantes](../../../entregas/APE-01-reporte-publicacion.pdf), páginas físicas 9–13, complementada con las comprobaciones del portafolio.

## Avance incorporado

Se registraron las diez categorías de OWASP Top 10:2025 y se construyó una matriz de ocho riesgos, diferenciando resultados confirmados de escenarios condicionados. A05 no tuvo inyección confirmada en los flujos probados; A08 no tuvo aceptación de software alterado demostrada. La referencia uv:latest se mantiene como observación de construcción relacionada con A03.

## Priorización de la entrega

1. A06: aceptación de tiempos negativos — impacto 3, probabilidad 2, riesgo 6.
2. A07: protección insuficiente de autenticación — impacto 3, probabilidad 2, riesgo 6.
3. A01: lectura de registros de equipos ajenos — impacto 2, probabilidad 2, riesgo 4.

La selección se justifica por integridad de resultados, protección de las cuentas y separación de permisos. Los riesgos condicionados suben de prioridad si se confirman en un despliegue.

## Entregables

- [Lista de cotejo](lista-cotejo-owasp.md).
- [Registro por categoría, rutas y archivos](registro-detallado-por-categoria.md).
- [Matriz para el reporte y tres seleccionados](matriz-priorizacion-para-reporte.md).
- [Capturas y resumen A06/A08/A09](HALLAZGOS-RESUMIDOS-A06-A08-A09.md).
- [Insumo para APE 02](insumo-ape-02.md).

## Precisiones de publicación

El documento original conserva formulaciones generales de A02/A04 como «confirmado». En los resúmenes del repositorio se mantienen las condiciones verificadas: no se ha demostrado producción con DEBUG expuesto ni que la clave local actual sea débil. Los avisos de SCA no equivalen a vulnerabilidades explotadas. No se introducen pruebas nuevas por importar el reporte.

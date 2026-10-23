# Entrega del reporte APE 01

[Reporte completo para publicación](APE-01-reporte-publicacion.pdf).

Documento fuente: `APE_ 01_ Análisis y superficie de ataque del proyecto.docx.pdf`, aportado por el usuario el 23/10/2026. La copia original permanece fuera del repositorio y no se sube a GitHub.

## Preparación de la copia pública

- Se conservan 16 páginas y el texto del documento.
- Se retiraron cinco capturas de las páginas físicas 10, 11 y 12 que muestran claves/tokens o pantallas de depuración potencialmente sensibles: A02, A04, A05, A07 y A10. Se sustituyeron por notas dentro del mismo espacio. La eliminación se aplica a los objetos de imagen, no sólo a una capa visual.
- Se conservan las capturas revisadas de A01, A03, A06, A08 y A09, además de las figuras generales de la fase 1.
- Las notas de publicación no modifican las conclusiones originales ni transforman indicios en nuevas comprobaciones.

Las referencias a página en el repositorio usan el orden físico 1–16. Los pies del documento original repiten una numeración de plantilla que no coincide con ese orden.

## Correspondencia del documento con las fases

| Páginas físicas | Parte del documento | Destino en el repositorio |
| --- | --- | --- |
| 1–2 | Datos y objetivos | Informe consolidado y ficha. |
| 2–6 | Selección, alcance, figuras e inventario | Fase 1. |
| 6–9 | Criterios CIA, activos, amenazas y controles | Fase 2. |
| 9–12 | Sección conjunta de errores y OWASP | Fase 3 y fase 4, con enlaces cruzados. |
| 12–13 | Priorización | Matriz de la fase 4. |
| 14–15 | Preguntas y conclusiones | Preguntas del documento e informe consolidado. |
| 15–16 | Rúbrica y bibliografía | PDF de referencia. |

## Notas de consistencia

- El reporte declara Django 6.0; las comprobaciones internas se hicieron con 5.2.8. El repositorio distingue ambas fuentes.
- La tabla enumera 12 activos, aunque las conclusiones mencionan diez.
- El documento dice 201 vulnerabilidades en un escaneo de requirements y 19 advertencias de check --deploy. El escaneo técnico disponible en el portafolio se hizo sobre paquetes instalados y contiene alias/duplicados. No se equiparan esos números ni se presenta una captura pequeña como prueba de todos los avisos.
- DEBUG en desarrollo, una clave de fallback en el código y tokens en una URL deben valorarse con las condiciones del despliegue; no se afirma un compromiso de producción.
- Dos declaraciones de refresh para la misma URL no son dos rutas efectivas independientes; prevalece la resolución del router.
- En A08 no se confirmó manipulación de software; latest se conserva como observación de construcción relacionada con A03.
- La duración de tokens no prueba por sí sola una vulnerabilidad. Las correcciones, revisión entre pares y cobertura de todas las rutas no se marcan como realizadas sin evidencia.

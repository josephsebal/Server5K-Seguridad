# Server5K — Portafolio de Software Security

**APE 01: Análisis y superficie de ataque del proyecto.** Universidad Nacional de Loja · Computación · Ciclo 8A · Unidad 1.

**Integrantes:** Darwin Enrique Granda Orosco · Darwin Andrés Sarango Soto · Joseph Sebastian Balcazar Loaiza.
**Docente:** Valeria Herrera Salazar.
**Período académico:** 28 de septiembre al 23 de octubre de 2026.

Aplicación auditada: [DarwinG23/Server5K](https://github.com/DarwinG23/Server5K). Este repositorio reúne el reporte, avances y evidencias de seguridad.

## Avance por fase

| Fase | Qué se incorporó del documento | Acceso |
| --- | --- | --- |
| **1. Selección y superficie** | Ficha del proyecto, alcance, inventario de 16 elementos y cuatro figuras. | [Ver fase 1](guias/ape-01/fase-01-seleccion-y-superficie/README.md) |
| **2. Activos y amenazas** | Matriz CIA de 12 activos, amenazas y dos controles propuestos por activo. | [Ver fase 2](guias/ape-01/fase-02-activos-y-amenazas/README.md) |
| **3. Gestión de errores** | Casos ejecutados, fugas observadas, registro de errores y propuestas de corrección. | [Ver fase 3](guias/ape-01/fase-03-gestion-de-errores/README.md) |
| **4. OWASP y priorización** | Diez categorías, matriz de riesgos, tres hallazgos seleccionados y capturas. | [Ver fase 4](guias/ape-01/fase-04-owasp-y-priorizacion/README.md) |

El documento se integró el **23/10/2026**. “Documentado” no equivale a “corregido”: se señalan pruebas no ejecutadas, límites del laboratorio, revisión entre pares pendiente y controles aún propuestos. No se reconstruyen fechas de ejecución ni commits de semanas anteriores.

## Documento y resultados principales

- [Reporte completo, copia preparada para publicación](entregas/APE-01-reporte-publicacion.pdf).
- [Procedencia del reporte y notas de publicación](entregas/README.md).
- [Informe consolidado](guias/ape-01/informe-consolidado.md).
- [Matriz de priorización y tres hallazgos de la entrega](guias/ape-01/fase-04-owasp-y-priorizacion/matriz-priorizacion-para-reporte.md).
- [Preguntas y respuestas del documento](guias/ape-01/preguntas-del-documento.md).
- [Hallazgos por categoría, rutas y archivos](guias/ape-01/fase-04-owasp-y-priorizacion/registro-detallado-por-categoria.md).
- [Capturas A06, A08 y A09 y explicaciones sencillas](guias/ape-01/fase-04-owasp-y-priorizacion/HALLAZGOS-RESUMIDOS-A06-A08-A09.md).

## Cómo repetir las pruebas

```bash
./probar-owasp.sh
# Mostrar sólo la explicación de una categoría (se ejecutan las 19 comprobaciones):
./probar-owasp.sh A01
```

Requiere el repositorio Server5K y sus dependencias en `../Server5K/.venv`; se puede indicar otra ruta con `SERVER5K_DIR`. Las pruebas crean cuentas, equipos y una base SQLite temporal, sin utilizar la base real. A03 no vuelve a consultar avisos CVE; A08 realiza revisión de configuración.

- [Guía sencilla](guias/ape-01/fase-04-owasp-y-priorizacion/GUIA-FACIL-PARA-PROBAR.md).
- [Demostraciones en Swagger](PRUEBAS-EN-SWAGGER.md).
- [Evidencias técnicas y procedimiento](guias/ape-01/fase-04-owasp-y-priorizacion/evidencias/revision-server5k/README.md).

## Continuidad del curso

[APE 02](guias/ape-02/README.md), [APE 03](guias/ape-03/README.md) y [APE 04](guias/ape-04/README.md) mantienen espacios reservados hasta recibir sus guías. Los formatos de trabajo del portafolio se adaptan a las plantillas del EVA cuando se proporcionen.

Las pruebas se limitan al entorno propio o controlado. Las capturas con claves/tokens o depuración sensible se retiraron de la copia pública del reporte; el original no se publica. El código funcional de la aplicación no se modifica desde este portafolio.

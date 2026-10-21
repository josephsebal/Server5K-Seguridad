# Server5K — Portafolio de seguridad

Repositorio de evidencias de Software Security, ciclo 8A, período 2026.
Aplicación objetivo: [Server5K](https://github.com/DarwinG23/Server5K).

## Estado

Estructura y plantillas creadas. La ficha contiene información identificada en el código. Los inventarios, matrices, pruebas y conclusiones están **pendientes de completar y validar**; no constituyen resultados de una auditoría realizada.

## Organización

```text
.
├── guias/
│   ├── ape-01/
│   │   ├── fase-01-seleccion-y-superficie/
│   │   ├── fase-02-activos-y-amenazas/
│   │   ├── fase-03-gestion-de-errores/
│   │   ├── fase-04-owasp-y-priorizacion/
│   │   ├── informe-consolidado.md
│   │   └── preguntas-de-control.md
│   ├── ape-02/
│   ├── ape-03/
│   └── ape-04/
├── referencias/
└── plantillas/
```

- [Guía APE 01 y lista de entrega](guias/ape-01/README.md)
- [Ficha del proyecto](guias/ape-01/fase-01-seleccion-y-superficie/ficha-proyecto.md)
- [Registro de evidencias](plantillas/registro-evidencias.md)
- [Guía original](referencias/guia-ape-01.pdf)

El PDF exige organización por guía y fase, pero no prescribe nombres exactos de carpetas. Esta es una propuesta de organización. Solo describe las fases de APE 01; APE 02–04 quedan reservadas, sin inventar sus fases. Las plantillas son propias y deberán ajustarse a las oficiales del EVA cuando estén disponibles.

## Cómo trabajar

1. Completar responsables y alcance; registrar versión y ejecución actual del entorno.
2. Documentar cada fase y guardar las evidencias en su carpeta `evidencias/`.
3. Relacionar activos `ACT-###`, elementos expuestos `SUP-###`, errores `ERR-###`, hallazgos `HAL-###` y evidencias `EVI-Fn-###`.
4. Adjuntar solo evidencias revisadas: ocultar contraseñas, tokens, cookies, datos personales y claves.
5. Actualizar el estado de los entregables y el informe consolidado antes de entregar.

El código de la aplicación se mantiene en su repositorio original. Este repositorio almacena el portafolio de auditoría; las correcciones pueden documentarse con enlaces a commits o parches revisados.

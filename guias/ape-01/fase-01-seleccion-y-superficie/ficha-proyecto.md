# Ficha del proyecto

Estado: primera versión basada en revisión del código; completar datos académicos y confirmar ejecución actual.

| Campo | Valor |
| --- | --- |
| Nombre | Server5K |
| Función | Gestión de competencias 5K, equipos, jueces y registros de tiempo con actualizaciones en tiempo real |
| Integrantes | Pendiente |
| Asignatura / ciclo | Software Security / 8A |
| Docente | Valeria Herrera Salazar |
| Código | https://github.com/DarwinG23/Server5K |
| Commit local de referencia | `826aec5c04dfc5d3f8be77e9abde2d13f69a51e8` |
| Entorno objetivo propuesto | Instalación local de laboratorio |

## Usuarios y roles identificados

- Administrador: gestión mediante Django Admin; permisos efectivos pendientes de comprobar.
- Juez: autenticación y gestión de registros de equipos; restricciones pendientes de comprobar.
- Visitante: consulta de vistas públicas de competencias y resultados.

## Tecnologías declaradas

Python >=3.13; Django; Django REST Framework; SimpleJWT; Channels y Daphne; PostgreSQL; Redis; WhiteNoise; drf-spectacular. Fuente: `pyproject.toml`, configuraciones y rutas del código objetivo. Registrar versiones efectivamente instaladas en `entorno.md`.

## Requisitos mínimos

- [x] Código fuente disponible.
- [x] Autenticación implementada en el código.
- [x] Configuración de base de datos disponible.
- [ ] Ejecución local comprobada y evidencia actual adjunta.
- [ ] Cuentas de prueba de administrador y usuario común creadas y verificadas.

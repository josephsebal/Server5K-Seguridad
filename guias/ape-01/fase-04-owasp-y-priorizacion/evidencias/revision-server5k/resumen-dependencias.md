# Resumen del escaneo de dependencias

Se analizaron 63 paquetes instalados, incluidas herramientas de desarrollo. En 17 se recibieron avisos. Los registros brutos pueden contener duplicados y alias, y no representan explotabilidad confirmada. El resto no obtuvo avisos en esta consulta, lo que no garantiza ausencia de fallos.

| Paquete | Versión instalada | Registros brutos (sin deduplicar) |
| --- | --- | --- |
| django | 5.2.8 | 55 |
| pyjwt | 2.10.1 | 21 |
| pygments | 2.19.2 | 2 |
| twisted | 25.5.0 | 3 |
| aiohttp | 3.13.2 | 72 |
| autobahn | 25.10.2 | 1 |
| cryptography | 46.0.3 | 13 |
| daphne | 4.2.1 | 4 |
| djangorestframework | 3.16.1 | 2 |
| idna | 3.11 | 2 |
| msgpack | 1.1.2 | 2 |
| multidict | 6.7.0 | 1 |
| pyopenssl | 25.3.0 | 4 |
| pyasn1 | 0.6.1 | 10 |
| pytest | 9.0.0 | 2 |
| setuptools | 80.9.0 | 2 |
| sqlparse | 0.5.3 | 10 |

Priorizar alcance real, distinguir dependencias de ejecución y de desarrollo y verificar correcciones con los proveedores. El informe verifica de forma independiente el aviso oficial de Django de diciembre de 2025. No se ejecutaron exploits de dependencias.

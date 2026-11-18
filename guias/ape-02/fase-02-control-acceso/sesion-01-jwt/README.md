# Sesión 1 · Análisis de tokens JWT

Pruebas realizadas el **12/11/2026, 10:24:35 (Ecuador)**. Publicación en el portafolio: **13/11/2026**.

- [Informe con redacción simplificada](informe.md).
- [Informe PDF actualizado: sesiones 1 y 2](../../../../entregas/APE-02-fase-02-control-acceso.pdf).
- [Documento editable](https://docs.google.com/document/d/18ekMniZCxJlJTltbczjbvmL5arOzhYUpAeWVBdrgBwg/edit).
- [Resultados originales del laboratorio](evidencias/resultados.json).
- [Captura de jwt.io](evidencias/E02-jwtio.png).
- [Script reproducible](analizar_jwt.py).

## Resultados

El token de acceso dura 60 minutos y el de renovación, 7 días. La firma del original se verificó y la ruta `/api/me/` respondió 200. Las variantes sin firma, alterada, vencida y sin `exp` recibieron 401. La clave fija de respaldo se documenta como riesgo condicionado a que el despliegue la utilice; no se comprobó producción.

## Alcance y procedencia

Se evaluó **DarwinG23/Server5K, commit `826aec5c04dfc5d3f8be77e9abde2d13f69a51e8`**, con Django 5.2.8, SimpleJWT 5.5.1 y PyJWT 2.10.1. APIClient ejecutó las vistas reales con SQLite en memoria y una cuenta ficticia. La carpeta `Server5K/` incorporada posteriormente al portafolio puede contener cambios: este informe no certifica esa versión ni sus correcciones.

La imagen contiene datos ficticios y una copia sin firma. No se publican contraseñas, claves de firma ni tokens completos reutilizables. Los identificadores E-01 a E-04 del registro inicial corresponden a obtención del token, decodificación, fechas y validación, respectivamente. La redacción final usa sus nombres completos.

## Repetir el laboratorio

Utilizar un checkout de la versión que se desea evaluar y su entorno Python con dependencias instaladas:

```bash
/ruta/Server5K/.venv/bin/python guias/ape-02/fase-02-control-acceso/sesion-01-jwt/analizar_jwt.py \
  --repo /ruta/Server5K \
  --output /tmp/server5k-jwt-nueva-ejecucion
```

El directorio de salida debe ser nuevo. El script genera una contraseña y clave temporal, crea una base en memoria y no modifica la base existente. Registra la revisión real y si hay cambios locales. Fechas e identificadores cambian al repetirlo; los archivos históricos no deben reemplazarse por resultados nuevos. Si se evalúa una versión diferente, se deben interpretar nuevamente sus resultados.

La sesión 2 y las pruebas IDOR no están incluidas en esta entrega.

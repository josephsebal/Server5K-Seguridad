# Insumo para APE 02

| Eje | Hallazgos / controles | Siguiente verificación |
| --- | --- | --- |
| Criptografía | HAL-008; PBKDF2 con sal observado | Exigir secreto al arranque, revisar rotación JWT y TLS del despliegue; no usar el valor real en evidencias |
| Control de acceso | HAL-001; HAL-006; WS rechaza ID de juez ajeno | Permisos por objeto, competencias distintas y matriz de roles; verificar privacidad de resultados |
| Inyecciones | P15 y P16 sin SQLi/XSS demostrado; HAL-009 con avisos | Ampliar revisión de entradas y salidas; analizar alcance real de CVEs sin extrapolar a todos los usos ORM |

Evidencias y condiciones: [informe](hallazgos-server5k.md). Las demás fases de APE 02 deben definirse con su guía oficial.

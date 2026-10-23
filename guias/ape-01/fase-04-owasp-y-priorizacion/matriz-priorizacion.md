# Matriz de priorización — revisión local

> Para la entrega académica del 23/10/2026, consultar la [matriz contextualizada al reporte](matriz-priorizacion-para-reporte.md). Separa condiciones de despliegue no comprobadas de los hallazgos reproducidos; esta tabla previa conserva la valoración de los escenarios técnicos.

Escala: impacto (I) y probabilidad (P) de 1 a 3; riesgo = I × P. 1–2 bajo, 3–4 medio, 6–9 alto. Evaluación cualitativa de laboratorio, no CVSS. Para riesgos condicionales se puntúa el escenario afectado, sin afirmar su presencia actual.

**Impacto:** 1 = revelación técnica limitada; 2 = exposición operativa o bloqueo parcial; 3 = corrupción de resultados o suplantación. **Probabilidad:** 1 = escenario no alcanzado; 2 = requiere cuenta/condiciones específicas; 3 = condición directa o clave conocida bajo el escenario señalado.

| ID | Categoría | Hallazgo | Estado | I | P | Riesgo | Justificación |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HAL-001 | A01:2025 | Lectura de registros de un equipo ajeno | Confirmado en prueba aislada | 2 | 2 | 4 | Impacto y requisitos detallados en el informe; requiere verificar y corregir el control indicado. |
| HAL-002 | A07:2025 | Login sin limitación de intentos en la aplicación | Confirmado en código y prueba acotada | 3 | 2 | 6 | Impacto y requisitos detallados en el informe; requiere verificar y corregir el control indicado. |
| HAL-003 | A07:2025 | El formulario de jueces acepta contraseñas débiles | Confirmado en validación del formulario | 3 | 2 | 6 | Impacto y requisitos detallados en el informe; requiere verificar y corregir el control indicado. |
| HAL-004 | A06:2025 | Tiempos negativos persistidos por el endpoint HTTP | Confirmado en prueba aislada | 3 | 2 | 6 | Impacto y requisitos detallados en el informe; requiere verificar y corregir el control indicado. |
| HAL-005 | A10:2025 | Un lote incompleto se guarda y bloquea el reenvío | Confirmado en prueba aislada | 2 | 2 | 4 | Impacto y requisitos detallados en el informe; requiere verificar y corregir el control indicado. |
| HAL-006 | A06:2025 | Se permite escribir tiempos en una competencia detenida | Confirmado en prueba aislada | 3 | 2 | 6 | Impacto y requisitos detallados en el informe; requiere verificar y corregir el control indicado. |
| HAL-007 | A10:2025 | Tipos JSON incorrectos provocan 500 o filtran detalles internos | Confirmado; trazas completas sólo con DEBUG=True | 2 | 2 | 4 | Impacto y requisitos detallados en el informe; requiere verificar y corregir el control indicado. |
| HAL-008 | A04:2025 | Clave JWT pública de fallback si falta SECRET_KEY | Código confirmado y escenario simulado; no afecta por defecto al .env local | 3 | 3 | 9 | Condicionado a usar la clave pública de fallback; no priorizar como explotación del entorno actual. |
| HAL-009 | A03:2025 | Dependencias instaladas con avisos y fuentes de versiones divergentes | SCA y revisión de archivos; explotación por CVE no demostrada | 3 | 2 | 6 | Impacto y requisitos detallados en el informe; alcance CVE pendiente. |
| HAL-010 | A09:2025 | Autenticación sin eventos de auditoría con identidad y alertas | Revisión estática y observación limitada de logs | 2 | 2 | 4 | Impacto y requisitos detallados en el informe; requiere verificar y corregir el control indicado. |

Ver [detalle, evidencias y mitigaciones](hallazgos-server5k.md). Todos los hallazgos siguen abiertos; no se implementaron correcciones. En empate se prioriza integridad de resultados y abuso del login. HAL-008 pasa a prioridad inmediata si se confirma el fallback en algún despliegue; HAL-009 requiere triage por alcance y entorno.

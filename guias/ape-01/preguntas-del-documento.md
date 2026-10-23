# Preguntas de control — transcripción del documento

Fuente: reporte completo, páginas físicas 14–15. Se conserva el contenido de los autores y los tiempos verbales del documento. La transcripción procede del texto extraído y puede conservar saltos de línea.

6.Preguntas de Control:
  1. La superficie de ataque de una aplicación web no se limita a sus páginas
      visibles: incluye formularios, parámetros, cabeceras y componentes de
      terceros. ¿Por qué un inventario exhaustivo de la superficie de ataque
      constituye el punto de partida de cualquier auditoría de seguridad, y qué
      riesgos implica omitir un componente del inventario?
      El inventario permite conocer todos los puntos por los cuales una persona o servicio
      puede interactuar con la aplicación, no solo sus páginas visibles incluyendo
      formularios, parámetros, API, autenticación, WebSockets, panel administrativo,
      servicios internos y dependencias, a partir de esa información se define qué se
      probará, con qué permisos y qué evidencias se requieren, en el caso nuestro el
      Server5K, inventariar tanto los endpoints de equipos como el canal WebSocket evita
      limitar la revisión a la interfaz pública, si se omite una ruta o componente, podrían
      permanecer sin revisar controles de acceso, exposición de tokens, entradas
      manipulables o configuraciones peligrosas, lo que genera una conclusión de
      seguridad incompleta.
  2. Al clasificar los activos con la tríada CIA, un mismo activo puede exigir
      controles distintos para la confidencialidad, la integridad y la disponibilidad.
      ¿Cómo determinaría usted qué pilar priorizar cuando los recursos son
      limitados? Justifique su respuesta con un ejemplo de su propio proyecto.
      La prioridad debe establecerse según el valor del activo, el daño de una vulneración y
      la probabilidad de que ocurra, considerando además las obligaciones y operaciones
      del sistema, en el Server5K se propone priorizar la integridad de los registros de
      tiempos y resultados, porque una modificación no autorizada alteraría la clasificación
      de los equipos y reduciría la confianza en la competencia, por eso, los primeros
      controles recomendados son autorizaciones por juez y equipo, validaciones en el
      servidor y un registro auditable de modificaciones. La disponibilidad sigue siendo
      importante durante una carrera, por lo que deben mantenerse respaldos y
      mecanismos de recuperación; la confidencialidad se refuerza en datos de cuentas y
      credenciales. Esta priorización deberá ajustarse si las pruebas muestran mayor
      exposición en otro activo.
  3. Los mensajes de error detallados facilitan la depuración durante el
      desarrollo, pero constituyen una fuga de información en producción. ¿Qué
      prácticas permiten conciliar ambas necesidades, y qué información concreta
      no debería revelar jamás un mensaje de error dirigido al usuario final?
      Para conciliar la necesidad de depurar errores durante el desarrollo y proteger la
      información en producción, es importante implementar un manejo seguro de errores.
      Durante el desarrollo, se pueden utilizar mensajes detallados y registros técnicos que
      faciliten la identificación y corrección de fallos. Sin embargo, en producción se debe
      desactivar el modo de depuración, mostrar mensajes de error genéricos y almacenar
      los detalles técnicos en registros seguros, accesibles únicamente para el personal
      autorizado. Además, se recomienda implementar un manejo centralizado de
      excepciones y utilizar códigos de referencia para identificar los errores. Los mensajes
      dirigidos al usuario final nunca deben revelar información sensible, como
      contraseñas, tokens de autenticación, consultas SQL, estructuras de bases de datos,
      rutas internas del servidor, configuraciones del sistema o datos personales. De esta
      manera, se facilita la detección y solución de problemas sin comprometer la
      seguridad del sistema ni proporcionar información que pueda ser aprovechada por
      posibles atacantes.
  4. El OWASP Top 10 es un documento de concientización, no un estándar de
      verificación. ¿Qué relación existe entre sus diez categorías de riesgo y las
      vulnerabilidades concretas observadas en su aplicación, y por qué la
      priorización de hallazgos debe considerar el impacto y la probabilidad, y no
      únicamente la severidad técnica?

            OWASP Top 10:2025 permite identificar los principales riesgos de seguridad en
            aplicaciones web, pero es necesario realizar pruebas para comprobar si existen en el
            sistema. En el caso del Server5K se analizarán problemas como el acceso no
            autorizado a registros, configuraciones inseguras, dependencias vulnerables,
            exposición de tokens y mensajes de error que revelen información interna. Para
            evaluar estos riesgos, se considera la probabilidad de que ocurran y el impacto que
            podrían tener en los datos, usuarios y funcionamiento del sistema. Con estos
            resultados, se seleccionarán los tres riesgos más importantes que requieren atención
            prioritaria.

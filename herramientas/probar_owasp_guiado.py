"""Presentación sencilla de las pruebas aisladas existentes. No inicia un servidor."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

project=Path(sys.argv[1]).resolve()
category=sys.argv[2].upper() if len(sys.argv)>2 else None
if len(sys.argv)>3 or (category and category not in [f'A{i:02}' for i in range(1,11)]):
    raise SystemExit('Uso: ./probar-owasp.sh [A01 ... A10]')
repo=Path(__file__).resolve().parents[1]
evidence=repo/'guias/ape-01/fase-04-owasp-y-priorizacion/evidencias/revision-server5k'
folder=Path(tempfile.mkdtemp(prefix='server5k-practica-'))
print('LABORATORIO SERVER5K',flush=True)
print('Se crean jueces, equipos y una base temporal. No necesitas encender el servidor.',flush=True)
print('Se ejecutan las 19 comprobaciones; el filtro sólo selecciona qué explicación mostrar.',flush=True)
print('Los datos de tu instalación no se utilizan. Espera unos segundos...\n',flush=True)
with (folder/'resultados.json').open('w') as out,(folder/'errores-controlados.log').open('w') as err:
    run=subprocess.run([sys.executable,str(evidence/'reproducir_pruebas.py'),str(project)],stdout=out,stderr=err)
if run.returncode:
    print(f'La ejecución no terminó. Consulta {folder / "errores-controlados.log"}')
    raise SystemExit(run.returncode)
data=json.loads((folder/'resultados.json').read_text())
r={x['id']:x for x in data['results']}
def show(cat,title,lines):
    if category and cat!=category:return
    print(f'{cat} — {title}')
    for line in lines:print('  '+line)
    print()
x=r['P01-IDOR']
show('A01','¿Puedo leer el equipo de otro juez?',[
    'Ruta: GET /api/equipos/2/registros/estado/',
    'Archivo: app/views/registro_views.py, EstadoEquipoRegistrosView.get.',
    f"Resultado: con el juez A, el estado del equipo B respondió {x['status']}; el detalle respondió {x['control_detail_status']}.",
    'Hallazgo reproducido: lectura ajena.' if x['status']==200 and x['control_detail_status']==404 else 'El resultado cambió: revisar el JSON antes de declarar un hallazgo.',
    'La corrección debe exigir que el equipo pertenezca al juez. Considerar qué resultados son públicos.' ])
x=r['P13-DEBUG']
show('A02','¿El error enseña información interna?',[
    'Ruta: POST /api/login/. Archivo: server/settings.py y app/views/auth_views.py.',
    f"Con DEBUG=True: HTTP {x['status']}; traza visible: {x['contains_traceback']}; ruta interna visible: {x['contains_project_path']}.",
    'Es un riesgo si se expone el modo desarrollo. Esta prueba no demuestra producción expuesta.' ])
lock=(project/'uv.lock').read_text(); req=(project/'requirements.txt').read_text()
show('A03','¿Mis dependencias están revisadas?',[
    'Archivos: uv.lock, requirements.txt y Dockerfile. No corresponde a una URL.',
    f"Django usado en esta ejecución: {data['django']}.",
    'El escaneo anterior está en evidencias/revision-server5k/pip-audit.json.',
    'Este comando NO vuelve a consultar avisos CVE. Revisar el escaneo y su fecha antes de usarlo.',
    'Comparación actual: lock contiene Django 5.2.8: '+str('version = "5.2.8"' in lock)+'; requirements fija Django 6.0: '+str('django==6.0\n' in req)+'.' ])
x=r['P04-WEAK-PASSWORD'];y=r['P17-DEFAULT-SIGNING']
show('A04','¿Se protegen las contraseñas y las claves?',[
    'Archivos: app/models/juez.py y server/settings.py.',
    f"Hash observado: {x['algorithm']}. No se imprime la contraseña ni su hash.",
    f"Simulando la clave pública de respaldo, GET /api/me/ respondió {y['status']}.",
    'El almacenamiento usa PBKDF2 con sal. El problema JWT sólo ocurre si el despliegue usa el respaldo público; no se usa tu secreto real.' ])
x=r['P15-SQLI'];y=r['P16-XSS-ESCAPE']
show('A05','¿Mi entrada se interpreta como SQL o HTML?',[
    'Rutas: POST /api/login/ y GET /equipo/6/.',
    'Archivos: app/views/auth_views.py y templates/app/equipo_detail.html.',
    f"Login con texto SQL: HTTP {x['status']}. Marcador HTML escapado: {y['escaped_marker_present']}.",
    'No se confirmó inyección en estos dos casos. Es control efectivo en lo probado, no seguridad total.' ])
x=r['P05-NEGATIVE'];y=r['P07-CLOSED-COMPETITION']
show('A06','¿Se respetan las reglas de la carrera?',[
    'Rutas: POST /api/equipos/3/registros/ y POST /api/equipos/5/registros/.',
    'Archivos: app/services/registro_service.py y app/views/registro_views.py.',
    f"Tiempos negativos: HTTP {x['status']}, guardados negativos: {sum(t<0 for t in x['stored'])}.",
    f"Competencia detenida: HTTP {y['status']}, guardados: {y['stored_count']}.",
    'Son hallazgos si se guardan tiempos negativos o se escribe en la competencia detenida.' ])
x=r['P03-LOGIN'];y=r['P04-WEAK-PASSWORD']
show('A07','¿El login frena intentos y exige buenas contraseñas?',[
    'Ruta: POST /api/login/. Formulario: JuezAdminForm en app/admin.py.',
    'Rechazos: '+str(x['failed_statuses'])+f"; intento correcto posterior: {x['successful_after']}.",
    f"El formulario acepta la contraseña sintética 123: {y['form_valid']}.",
    'Seis rechazos no prueban un límite infinito: contrastar con la ausencia de throttle en el código. El formulario se prueba directamente, no por navegador.' ])
docker=(project/'Dockerfile').read_text()
show('A08','¿La aplicación verifica lo que descarga?',[
    'No se identificó un actualizador propio para reproducir el instalador de la simulación.',
    'Archivo de construcción: Dockerfile. Usa uv:latest: '+str('ghcr.io/astral-sh/uv:latest' in docker)+'.',
    'No aplica ese flujo concreto del instalador al módulo revisado. La etiqueta movible es una observación de construcción, no una descarga manipulada demostrada.' ])
x=r['P03-LOGIN']
show('A09','¿Puedo investigar los intentos fallidos?',[
    'Ruta: POST /api/login/. Archivos: app/views/auth_views.py y server/settings.py.',
    'Eventos capturados durante los intentos:',
    *[line for line in x['captured_log'].splitlines()],
    'Estos mensajes no identifican la cuenta intentada ni su origen. Hay logs, pero falta contexto de auditoría en el login; monitoreo externo no examinado.' ])
x=r['P06-PARTIAL'];y=r['P11-BATCH-ITEMS']
show('A10','¿Un dato incorrecto se rechaza sin romper la operación?',[
    'Rutas: POST /api/login/ y POST /api/equipos/{id}/registros/.',
    'Archivos: app/views/auth_views.py, app/views/registro_views.py y app/services/registro_service.py.',
    f"Login con lista JSON: HTTP {r['P09-LOGIN-LIST']['status']}.",
    f"Registros con tipo número: HTTP {r['P10-BATCH-TYPE']['status']}.",
    f"Lote incompleto: HTTP {x['status']}; tiempos guardados: {x['count']}; reintento: HTTP {x['retry_status']}.",
    'Detalle devuelto al enviar cadenas: '+str(y['response'].get('error',[{}])[0].get('error')),
    'Debe responder 400 por entradas inválidas y guardar todo el lote o ninguno.' ])
print('Códigos: 200=consulta exitosa; 201=guardado; 400=entrada rechazada; 401=falta autenticación; 403/404=acceso denegado/recurso no visible; 429=límite; 500=fallo interno.')
print(f'JSON completo: {folder / "resultados.json"}')
print(f'Errores controlados: {folder / "errores-controlados.log"}')
print('Una respuesta 500 esperada durante estas pruebas no significa que el script haya fallado.')

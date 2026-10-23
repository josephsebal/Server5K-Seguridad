"""Pruebas locales aisladas. Ejecutar con el Python del proyecto y ruta de su código como argumento."""
import sys, os, json, tempfile, logging, io, secrets, asyncio
from pathlib import Path
from datetime import datetime, timezone
project=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(project))
os.environ['DJANGO_SETTINGS_MODULE']='server.settings'
os.environ['SECRET_KEY']=secrets.token_urlsafe(48)
os.environ['DEBUG']='False'
# No cargar .env ni utilizar base de datos o Redis reales.
from django.conf import settings
work=tempfile.TemporaryDirectory(prefix='server5k-audit-')
settings.DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':str(Path(work.name)/'audit.sqlite3')}}
settings.CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}}
settings.ALLOWED_HOSTS=['testserver','localhost','127.0.0.1']
import copy
settings.LOGGING=copy.deepcopy(settings.LOGGING)
settings.LOGGING['handlers']['file']['filename']=str(Path(work.name)/'audit-django.log')
settings.STATIC_ROOT=Path(work.name)/'static'
import django
django.setup()
from django.core.management import call_command
call_command('migrate',verbosity=0)
from django.utils import timezone as tz
from app.models import Juez, Equipo, Competencia, RegistroTiempo
from rest_framework.test import APIClient
from django.test import override_settings
from django.contrib.auth.hashers import identify_hasher
from app.admin import JuezAdminForm
from rest_framework_simplejwt.tokens import AccessToken
results=[]
def record(id, **data): results.append({'id':id,**data})
def safe(resp):
 try: return resp.json()
 except Exception: return {'html': True,'bytes':len(resp.content)}
run=Competencia.objects.create(name='Auditoria sintetica en curso',datetime=tz.now(),is_running=True)
stop=Competencia.objects.create(name='Auditoria sintetica detenida',datetime=tz.now(),is_running=False,is_active=False)
pw=secrets.token_urlsafe(20)
a=Juez(username='audit_juez_a');a.set_password(pw);a.save()
b=Juez(username='audit_juez_b');b.set_password(pw);b.save()
def team(name,n,judge=a,competition=run):
 return Equipo.objects.create(name=name,number=n,judge=judge,competition=competition)
own=team('Equipo A',1)
other=team('Equipo B',2,b)
private=RegistroTiempo.objects.create(team=other,time=222000)
c=APIClient(raise_request_exception=False)
anon=APIClient(raise_request_exception=False)
login=c.post('/api/login/',{'username':a.username,'password':pw},format='json')
assert login.status_code==200,safe(login)
c.credentials(HTTP_AUTHORIZATION='Bearer '+login.json()['access'])
resp=c.get(f'/api/equipos/{other.id}/registros/estado/')
control=c.get(f'/api/equipos/{other.id}/')
record('P01-IDOR',request=f'GET /api/equipos/{other.id}/registros/estado/',actor='juez A, equipo asignado a juez B',status=resp.status_code,response=safe(resp),control_detail_status=control.status_code)
record('P02-ANON',status=anon.get(f'/api/equipos/{other.id}/registros/estado/').status_code)
# Sólo 6 intentos fallidos, sin carga ni fuerza bruta.
logbuf=io.StringIO(); handler=logging.StreamHandler(logbuf);root=logging.getLogger();root.addHandler(handler)
failed=[anon.post('/api/login/',{'username':a.username,'password':'incorrecta-sintetica'},format='json').status_code for _ in range(6)]
follow=anon.post('/api/login/',{'username':a.username,'password':pw},format='json')
root.removeHandler(handler)
record('P03-LOGIN',failed_statuses=failed,successful_after=follow.status_code,throttle_classes=settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_CLASSES',[]),captured_log=logbuf.getvalue(),note='No se observó bloqueo en 6 intentos; no prueba la ausencia de un proxy externo.')
form=JuezAdminForm(data={'username':'audit_weak','password1':'123','password2':'123','is_active':True})
valid=form.is_valid()
record('P04-WEAK-PASSWORD',form_valid=valid,form_errors=dict(form.errors),algorithm=identify_hasher(a.password).algorithm,password_validators_configured=len(settings.AUTH_PASSWORD_VALIDATORS))
negative=team('Negativos',3)
resp=c.post(f'/api/equipos/{negative.id}/registros/',{'registros':[{'tiempo':-1000} for _ in range(15)]},format='json')
record('P05-NEGATIVE',status=resp.status_code,stored=list(RegistroTiempo.objects.filter(team=negative).values_list('time',flat=True)),response=safe(resp))
partial=team('Parcial',4)
resp=c.post(f'/api/equipos/{partial.id}/registros/',{'registros':[{'tiempo':1000}]+[{} for _ in range(14)]},format='json')
retry=c.post(f'/api/equipos/{partial.id}/registros/',{'registros':[{'tiempo':1000} for _ in range(15)]},format='json')
record('P06-PARTIAL',status=resp.status_code,count=RegistroTiempo.objects.filter(team=partial).count(),response=safe(resp),retry_status=retry.status_code,retry_response=safe(retry))
closed=team('Competencia cerrada',10,competition=stop)
resp=c.post(f'/api/equipos/{closed.id}/registros/',{'registros':[{'tiempo':1000} for _ in range(15)]},format='json')
record('P07-CLOSED-COMPETITION',target_is_running=stop.is_running,other_assigned_competition_running=run.is_running,status=resp.status_code,stored_count=RegistroTiempo.objects.filter(team=closed).count())
# Errores controlados de tipos y recursos. Nunca guardar páginas DEBUG completas.
for ident,path,body in [('P08-LOGIN-EMPTY','/api/login/',{}),('P09-LOGIN-LIST','/api/login/',['invalido']),('P10-BATCH-TYPE',f'/api/equipos/{own.id}/registros/',{'registros':15}),('P11-BATCH-ITEMS',f'/api/equipos/{own.id}/registros/',{'registros':['x']*15}),('P12-REFRESH-TYPE','/api/token/refresh/',{'refresh':['invalido']})]:
 client=c if 'BATCH' in ident else anon
 with override_settings(DEBUG=False): resp=client.post(path,body,format='json')
 record(ident,status=resp.status_code,response=safe(resp))
with override_settings(DEBUG=True):
 resp=anon.post('/api/login/',['invalido'],format='json')
 text=resp.content.decode(errors='replace')
 record('P13-DEBUG',status=resp.status_code,contains_traceback='Traceback' in text,contains_project_path=str(project) in text,contains_attribute_error='AttributeError' in text,html_not_saved=True)
resp=anon.get('/audit-no-existe/')
record('P14-NOTFOUND',status=resp.status_code,headers={k:v for k,v in resp.items() if k.lower() in ['x-frame-options','x-content-type-options','referrer-policy','content-security-policy','strict-transport-security']})
# Login con entrada SQL: debe fallar y no autenticar.
resp=anon.post('/api/login/',{'username':"' OR 1=1 --",'password':'x'},format='json')
record('P15-SQLI',status=resp.status_code,response=safe(resp),note='Una entrada de prueba; no equivale a una auditoría exhaustiva de inyecciones.')
# Escape HTML en vistas públicas con marcador inocuo.
marker='<script>audit_marker_no_ejecutar</script>'
xss=team(marker,20)
with override_settings(STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}}):
 resp=anon.get(f'/equipo/{xss.id}/')
html=resp.content.decode(errors='replace')
record('P16-XSS-ESCAPE',status=resp.status_code,raw_marker_present=marker in html,escaped_marker_present='&lt;script&gt;audit_marker_no_ejecutar&lt;/script&gt;' in html)
# Riesgo condicional: clave de fallback del código, no la de .env.
import jwt
fallback='django-insecure-dev-key-change-in-production'
with override_settings(SECRET_KEY=fallback,SIMPLE_JWT={**settings.SIMPLE_JWT,'SIGNING_KEY':fallback}):
 from rest_framework_simplejwt.state import token_backend
 from unittest.mock import patch
 with patch.object(token_backend,'signing_key',fallback),patch.object(token_backend,'prepared_signing_key',fallback):
  payload={'token_type':'access','exp':int(tz.now().timestamp())+60,'iat':int(tz.now().timestamp()),'jti':secrets.token_hex(16),'juez_id':a.id}
  forged=jwt.encode(payload,fallback,algorithm='HS256')
  test=APIClient();test.credentials(HTTP_AUTHORIZATION='Bearer '+forged)
  rr=test.get('/api/me/')
  record('P17-DEFAULT-SIGNING',scenario='Sólo cuando falta SECRET_KEY y se utiliza el fallback público del código',status=rr.status_code,affects_current_env_not_tested=True)
# Reglas JWT del WS: rechazo de ID ajeno y ausencia de token.
async def ws_checks():
 from channels.testing import WebsocketCommunicator
 from server.asgi import application
 token=str(AccessToken(login.json()['access']))
 for ident,path in [('P18-WS-NO-TOKEN',f'/ws/juez/{a.id}/'),('P19-WS-OTHER-JUDGE',f'/ws/juez/{b.id}/?token={token}')]:
  ws=WebsocketCommunicator(application,path)
  connected,code=await ws.connect()
  record(ident,connected=connected,close_code=code)
  await ws.disconnect()
asyncio.run(ws_checks())
output={'executed_at_utc':datetime.now(timezone.utc).isoformat(),'django':django.get_version(),'database':'SQLite temporal independiente (no PostgreSQL de la aplicación)','channels':'InMemoryChannelLayer (no Redis real)','code_root':str(project),'results':results}
print(json.dumps(output,ensure_ascii=False,indent=2))
work.cleanup()

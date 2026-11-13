import os,sys,secrets,json,base64,argparse,subprocess
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
parser=argparse.ArgumentParser(description='Laboratorio JWT local con SQLite en memoria.')
parser.add_argument('--repo',required=True,type=Path,help='Checkout de Server5K que se desea evaluar')
parser.add_argument('--output',required=True,type=Path,help='Directorio nuevo para los resultados, sin sobrescribir evidencias')
args=parser.parse_args()
REPO=args.repo.resolve()
if not (REPO/'manage.py').is_file():
 parser.error('--repo debe contener manage.py')
args.output.mkdir(parents=True,exist_ok=False)
revision=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
modified=bool(subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True).strip())
sys.path.insert(0,str(REPO))
os.environ['DJANGO_SETTINGS_MODULE']='server.settings'
os.environ['SECRET_KEY']=secrets.token_urlsafe(64)
os.environ.pop('POSTGRES_DB',None)
from django.conf import settings
settings.DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':':memory:'}}
settings.ALLOWED_HOSTS=['testserver','localhost']
settings.SECURE_SSL_REDIRECT=False
settings.LOGGING={'version':1,'disable_existing_loggers':True}
import django
django.setup()
from django.core.management import call_command
call_command('migrate',verbosity=0)
from app.models import Juez
from rest_framework.test import APIClient
import jwt,rest_framework_simplejwt
p=secrets.token_urlsafe(24)
u=Juez(username='juez_laboratorio_ape02',first_name='Cuenta',last_name='Laboratorio',email='laboratorio@example.invalid')
u.set_password(p);u.save()
c=APIClient()
r=c.post('/api/login/',{'username':u.username,'password':p},format='json')
assert r.status_code==200,r.data
access=r.data['access'];refresh=r.data['refresh']
def decode(t):
 return json.loads(base64.urlsafe_b64decode(t.split('.')[1]+'=='))
a=decode(access);b=decode(refresh)
verified=jwt.decode(access,settings.SECRET_KEY,algorithms=['HS256'])
def probe(t):
 c.credentials(HTTP_AUTHORIZATION='Bearer '+t)
 res=c.get('/api/me/')
 return {'http_status':res.status_code,'body':res.json()}
tests={'original':probe(access)}
tests['alg_none']=probe(jwt.encode(a,key='',algorithm='none'))
mut=dict(a);mut['username']='alterado_sin_firma'
seg=base64.urlsafe_b64encode(json.dumps(mut,separators=(',',':')).encode()).decode().rstrip('=')
tests['payload_alterado']=probe(access.split('.')[0]+'.'+seg+'.'+access.split('.')[2])
for name,payload in [('expirado',dict(a,exp=a['iat']-1)),('sin_exp',{k:v for k,v in a.items() if k!='exp'})]:
 tests[name]=probe(jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256'))
def times(payload):
 return {k:{'unix':payload[k],'utc':datetime.fromtimestamp(payload[k],timezone.utc).isoformat(),'ecuador':datetime.fromtimestamp(payload[k],ZoneInfo('America/Guayaquil')).isoformat()} for k in ['iat','exp']}
out={'captured_at':datetime.now(ZoneInfo('America/Guayaquil')).isoformat(),'repo_commit':revision,'working_tree_modified':modified,'environment':'Django APIClient; SQLite en memoria; clave y contraseña aleatorias efímeras; sin conexión a producción','versions':{'django':django.get_version(),'pyjwt':jwt.__version__,'simplejwt':rest_framework_simplejwt.__version__},'request':{'method':'POST','path':'/api/login/','username':u.username,'password':'[OCULTA]'},'response':{'http_status':r.status_code,'access':'[TOKEN OMITIDO]','refresh':'[TOKEN OMITIDO]'},'access_header':jwt.get_unverified_header(access),'access_claims':a,'refresh_header':jwt.get_unverified_header(refresh),'refresh_claims':b,'access_time':times(a),'refresh_time':times(b),'access_lifetime_seconds':a['exp']-a['iat'],'refresh_lifetime_seconds':b['exp']-b['iat'],'signature_verified':verified==a,'tests':tests}
dest=args.output
(dest/'resultados.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
# Sólo cabecera y payload públicos del usuario ficticio para el decodificador.
# No se guardan tokens completos ni claves de firma.
print(json.dumps(out,indent=2,ensure_ascii=False))

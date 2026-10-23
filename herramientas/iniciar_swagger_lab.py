import sys,os,tempfile,copy
from pathlib import Path
project = Path(__file__).resolve().parents[2] / 'Server5K'
sys.path.insert(0,str(project))
os.environ['DJANGO_SETTINGS_MODULE']='server.settings'
import secrets
os.environ['SECRET_KEY']=secrets.token_urlsafe(48)
os.environ['DEBUG']='False'
from django.conf import settings
lab=Path(tempfile.mkdtemp(prefix='server5k-swagger-'))
settings.DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':str(lab/'lab.sqlite3')}}
settings.CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}}
settings.ALLOWED_HOSTS=['localhost','127.0.0.1']
settings.LOGGING=copy.deepcopy(settings.LOGGING)
settings.LOGGING['handlers']['file']['filename']=str(lab/'django.log')
settings.STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}}
settings.STATIC_ROOT=lab/'static';settings.STATIC_ROOT.mkdir()
import django
django.setup()
from django.core.management import call_command
call_command('migrate',verbosity=0)
from app.models import Juez,Equipo,Competencia,RegistroTiempo
from django.utils import timezone
active=Competencia.objects.create(name='LAB Competencia activa',datetime=timezone.now(),is_running=True)
closed=Competencia.objects.create(name='LAB Competencia detenida',datetime=timezone.now(),is_running=False,is_active=False)
a=Juez(username='juez_demo_a');a.set_password('Laboratorio5K!2026');a.save()
b=Juez(username='juez_demo_b');b.set_password('Laboratorio5K!2026');b.save()
for name,n,judge,comp in [('LAB Equipo A',1,a,active),('LAB Equipo B',2,b,active),('LAB Negativos',3,a,active),('LAB Parcial',4,a,active),('LAB Detenida',5,a,closed)]:
 Equipo.objects.create(name=name,number=n,judge=judge,competition=comp)
RegistroTiempo.objects.create(team_id=2,time=222000)
# Documentar el cuerpo en Swagger sin cambiar validación ni lógica funcional.
from app.views.registro_views import RegistrarTiemposView
from drf_spectacular.utils import extend_schema,OpenApiExample
from rest_framework import serializers
class LabBatchSerializer(serializers.Serializer):
 registros=serializers.ListField(child=serializers.DictField())
RegistrarTiemposView.post=extend_schema(request=LabBatchSerializer,examples=[OpenApiExample('15 tiempos de ejemplo',value={'registros':[{'tiempo':1000} for _ in range(15)]},request_only=True)])(RegistrarTiemposView.post)
settings.SPECTACULAR_SETTINGS={**settings.SPECTACULAR_SETTINGS,'TITLE':'Server5K — LABORATORIO AISLADO','DESCRIPTION':'Datos ficticios. Sin acceso a la base real. Juez A: juez_demo_a. Contraseña de laboratorio: Laboratorio5K!2026. Equipos: 1 propio, 2 ajeno, 3 negativos, 4 parcial, 5 competencia detenida.'}
print('LAB_DIR='+str(lab),flush=True)
from daphne.cli import CommandLineInterface
CommandLineInterface().run(['-b','127.0.0.1','-p','8000','server.asgi:application'])

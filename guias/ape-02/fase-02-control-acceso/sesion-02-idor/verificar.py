"""Ejecuta las siete pruebas existentes con SQLite en memoria y secretos efímeros."""
import os
import secrets
import sys
from pathlib import Path
repo = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo / "Server5K"))
os.environ["DJANGO_SETTINGS_MODULE"] = "server.settings"
os.environ["SECRET_KEY"] = secrets.token_urlsafe(64)
os.environ["ENABLE_HTTPS"] = "False"
from django.conf import settings
settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
settings.ALLOWED_HOSTS = ["testserver", "localhost"]
settings.LOGGING = {"version": 1, "disable_existing_loggers": True}
import django
django.setup()
from django.core.management import call_command
call_command("test", "app.tests.tests.AuthorizationSecurityTests", verbosity=2, interactive=False)

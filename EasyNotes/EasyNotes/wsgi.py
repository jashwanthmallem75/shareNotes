"""
WSGI config for EasyNotes project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyNotes.EasyNotes.settings')

application = get_wsgi_application()

# In production, wrap the application with WhiteNoise to serve static and media files.
if not settings.DEBUG:
    application = WhiteNoise(application, root=settings.STATIC_ROOT)
    application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)

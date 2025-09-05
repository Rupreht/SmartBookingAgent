"""
ASGI config for sba project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartbookingagent.settings")

# for only https://www.netangels.ru, it is not possible to rename the asgi variable to application
app = get_asgi_application()

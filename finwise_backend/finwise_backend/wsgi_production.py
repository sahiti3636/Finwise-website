"""
WSGI config for finwise_backend production deployment.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finwise_backend.settings_production')

application = get_wsgi_application() 
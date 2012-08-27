
__author__ = 'Chris Barbara'

import os
import sys


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from django.conf import settings
_ = settings.TEMPLATE_DIRS

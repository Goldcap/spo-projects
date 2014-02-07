import os
import sys

paths = [ '/var/www',
          '/var/www/html/sites/dev.specialprojectoffice.com/spo-project',
          '/usr/local/lib/python2.7/site-packages',
]

for path in paths:
    if path not in sys.path:
        sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'spo_site.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

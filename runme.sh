#!/bin/bash

/var/venvs/usm/bin/activate

python manage.py runserver 192.168.2.107:8011

exit 0

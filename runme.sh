#!/bin/bash

/var/venvs/spo/bin/activate

python manage.py runserver 127.0.0.1:8016

exit 0

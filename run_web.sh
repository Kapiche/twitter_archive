#!/bin/sh

cd /home/docker/code
python manage.py migrate
supervisord -n

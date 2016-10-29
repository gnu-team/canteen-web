#!/bin/bash
exec uwsgi --module canteen_web.wsgi:application -s sock --umask 0

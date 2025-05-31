#!/bin/sh

cd /app/library_system

celery -A library_system beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
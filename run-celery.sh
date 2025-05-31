#!/bin/sh

cd /app/library_system

celery -A library_system worker --loglevel=info

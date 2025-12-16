#!/usr/bin/env bash

# script called by the Scalingo Procfile

DB_CHECK_SCHEMA=false gunicorn --workers "${NB_API_WORKERS:-5}" --threads "${NB_API_THREADS:-4}" -b ":$PORT" 'geovisio:create_app()'

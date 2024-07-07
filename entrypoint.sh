#!/bin/bash

flask db upgrade

gunicorn -w 3 --threads 3 -b 0.0.0.0:7111 run:app

exec "$@"
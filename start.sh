#!/bin/sh

pip install -r requirements.txt
alembic upgrade head
granian \
  --interface asgi \
  --host 0.0.0.0 \
  --port 443 \
  --workers 4 \
  --ssl-certificate <FILE> \
  --ssl-keyfile <FILE> \
  --ssl-protocol-min tls1.3 \
  --no-ws \
  --no-log \
  main:app

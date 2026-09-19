#!/bin/sh

pip install -r requirements.txt --no-cache-dir
python -B -S -X dev run_sqlite.py
python -B -S -X dev telegram_bot.py &
granian \
  --interface asgi \
  --host 0.0.0.0 \
  --port 443 \
  --workers 3 \
  --ssl-certificate <FILE> \
  --ssl-keyfile <FILE> \
  --ssl-protocol-min tls1.3 \
  --no-ws \
  --no-log \
  main:app

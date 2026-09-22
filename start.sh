#!/bin/sh

export $(cat .env | xargs) # LF(no CRLF)
pip install -r requirements.txt --no-cache-dir
python -B -O run_sqlite.py
python -B -O telegram_bot.py &
granian \
  --interface asgi \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 1 \
  --no-ws \
  main:app

#granian \
#  --interface asgi \
#  --host 0.0.0.0 \
#  --port 443 \
#  --workers 3 \
#  --ssl-certificate <FILE> \
#  --ssl-keyfile <FILE> \
#  --ssl-protocol-min tls1.3 \
#  --no-ws \
#  --no-log \
#  main:app

#!/bin/bash
mkdir -p keys
#openssl \

openssl \
    req -x509 -sha256 -nodes -days 365 \
    -newkey rsa:2048 -keyout keys/server.key -out keys/server.crt

openssl \
    req -new -x509 -keyout keys/server.pem \
    -out keys/server.pem -days 365 -nodes
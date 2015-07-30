#!/usr/bin/env bash
set -ex
export UC_DOMAIN=mooc.enight.me

[ -e certs ] || mkdir certs
cd certs
echo "Creating ca keys..."
echo 01 > ca.srl
openssl genrsa -des3 -out ca-key.pem
openssl rsa -in ca-key.pem -out ca-key.pem
openssl req -subj "/CN=$UC_DOMAIN/" -new -x509 -days 365 -key ca-key.pem -out ca.pem

echo "Creating server keys..."
openssl genrsa -des3 -out server-key.pem
openssl rsa -in server-key.pem -out server-key.pem
openssl req -subj "/CN=$UC_DOMAIN/" -new -key server-key.pem -out server.csr
openssl x509 -req -days 365 -in server.csr -CA ca.pem -CAkey ca-key.pem -out server-cert.pem

echo "Creating client keys..."
openssl genrsa -des3 -out key.pem
openssl rsa -in key.pem -out key.pem
openssl req -subj '/CN=*/' -new -key key.pem -out client.csr
echo extendedKeyUsage = clientAuth > extfile.cnf
openssl x509 -req -days 365 -in client.csr -CA ca.pem -CAkey ca-key.pem -out cert.pem -extfile extfile.cnf

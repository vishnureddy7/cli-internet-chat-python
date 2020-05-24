#/bin/sh

python -c 'import rsa_enc_dec; rsa_enc_dec.generate_rsa_keys()'

echo "Keys generated successfully"

python server.py &

echo "server started"

for i in {1..20}
do
  sleep 0.3
  python client.py &
  echo "client ${i} started"
done

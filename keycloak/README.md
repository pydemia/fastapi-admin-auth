
```bash
docker run --rm \
    -p 10000:8080 \
    -e KEYCLOAK_ADMIN=admin \
    -e KEYCLOAK_ADMIN_PASSWORD=admin \
    quay.io/keycloak/keycloak:24.0.2 \
    start-dev

```

```bash
mkdir certs && cd certs
```

```bash
/opt/keycloak/bin/kc.sh \
  export \
  --file fastapi-admin-auth-realm.json \
  --realm fastapi-admin-auth

```
#!/bin/bash

KEYCLOAK_CONTAINER_NAME="nomad_guiapi_keycloak" 

docker exec -it "$KEYCLOAK_CONTAINER_NAME" sh -c \
  "cp -rp /opt/keycloak/data/h2 /tmp ; \
  /opt/keycloak/bin/kc.sh export
    --dir /opt/keycloak/data/import \
    --db dev-file \
    --db-url 'jdbc:h2:file:/tmp/h2/keycloakdb;NON_KEYWORDS=VALUE'"

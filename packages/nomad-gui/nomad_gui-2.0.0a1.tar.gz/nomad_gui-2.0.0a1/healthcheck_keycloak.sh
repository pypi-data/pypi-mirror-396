#!/bin/bash

MANAGEMENT_URL="http://localhost:9000/${KC_HTTP_RELATIVE_PATH}"

/opt/keycloak/bin/kcadm.sh config credentials \
	--server "$MANAGEMENT_URL" \
	--realm master

/opt/keycloak/bin/kcadm.sh get "$MANAGEMENT_URL/health/live"

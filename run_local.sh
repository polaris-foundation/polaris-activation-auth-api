#!/bin/bash
SERVER_PORT=${1-5000}
export SERVER_PORT=${SERVER_PORT}
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_USER=dhos-activation-auth-api
export DATABASE_PASSWORD=dhos-activation-auth-api
export DATABASE_NAME=dhos-activation-auth-api
export FLASK_APP=dhos_activation_auth_api/autoapp.py
export ENVIRONMENT=DEVELOPMENT
export ALLOW_DROP_DATA=true
export IGNORE_JWT_VALIDATION=true
export IGNORE_CLINICIAN_JWT_VALIDATION=False
export AUTH0_AUDIENCE=https://dev.sensynehealth.com/
export REDIS_INSTALLED=False
export PROXY_URL=http://localhost
export HS_KEY=secret
export RABBITMQ_DISABLED=true
export MOCK_GDM_PATIENT_SCOPE="read:gdm_patient_abbreviated read:gdm_message write:gdm_message read:gdm_bg_reading write:gdm_bg_reading read:gdm_medication read:gdm_question read:gdm_answer write:gdm_answer read:gdm_trustomer read:gdm_telemetry write:gdm_telemetry write:gdm_terms_agreement"
export MOCK_SEND_ENTRY_CLINICIAN_SCOPE="read:send_clinician read:send_patient read:send_observation write:send_observation"
export MOCK_SEND_ENTRY_DEVICE_SCOPE="read:send_entry_identifier"
export TOKEN_URL=https://draysonhealth-sandbox.eu.auth0.com/oauth/token
export AUTH0_MGMT_CLIENT_ID=someid
export AUTH0_MGMT_CLIENT_SECRET=secret
export AUTH0_AUTHZ_CLIENT_ID=someid
export AUTH0_AUTHZ_CLIENT_SECRET=secret
export AUTH0_CLIENT_ID=someid
export NONCUSTOM_AUTH0_DOMAIN=https://draysonhealth-sandbox.eu.auth0.com
export CUSTOMER_CODE=DEV
export AUTH0_AUDIENCE=https://dev.sensynehealth.com
export LOG_FORMAT=COLOUR
export LOG_LEVEL=DEBUG


if [ -z "$*" ]
then
   flask db upgrade
   python -m dhos_activation_auth_api
else
  flask "$@"
fi

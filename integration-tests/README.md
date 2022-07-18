# DHOS Activation Auth API Integration Tests
Service-level integration tests for the DHOS Activation Auth API.

## Running the tests
```
# build containers
$ docker-compose build

# run tests
$ docker-compose up --abort-on-container-exit --exit-code-from dhos-activation-auth-integration-tests

# inspect test logs
$ docker logs dhos-activation-auth-integration-tests

# cleanup
$ docker-compose down
```

## Test development
For test development purposes you can keep the service running and keep re-running only the tests:
```
# in one terminal screen, or add `-d` flag if you don't want the process running in foreground
$ docker-compose up --force-recreate

# in another terminal screen you can now run the tests
$ DHOS_ACTIVATION_AUTH_BASE_URL="http://localhost:5000" \
  DATABASE_HOST=localhost \
  SYSTEM_JWT_SCOPE="write:gdm_activation write:send_device write:send_clinician read:send_device" \
  RABBITMQ_HOST=localhost \
  RABBITMQ_USERNAME=guest \
  RABBITMQ_PASSWORD=guest \
  behave --no-capture --logging-level DEBUG

# Don't forget to clean up when done!
$ docker-compose down
```

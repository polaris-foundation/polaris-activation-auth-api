import pytest
from flask import Flask
from flask.testing import FlaskClient

from dhos_activation_auth_api.helpers.utils import (
    generate_secure_random_string,
    hash_ascii_with_salt,
)
from dhos_activation_auth_api.models.device import Device, db


class TestDeviceJWT:
    def test_returns_403_when_device_does_not_exist(self, client: FlaskClient) -> None:
        response = client.get(
            "/dhos/v1/device/nope/jwt",
            headers={"x-authorisation-code": "some-code"},
        )
        assert response.status_code == 403

    def test_returns_400_when_missing_json_body(self, client: FlaskClient) -> None:
        uuid = "12345"
        device = Device(uuid=uuid, location_id="L1", description="some description")

        db.session.add(device)
        db.session.commit()

        response = client.get(f"/dhos/v1/device/{uuid}/jwt")
        assert response.status_code == 400

    def test_returns_400_when_json_body_missing_auth_code(
        self, client: FlaskClient
    ) -> None:
        uuid = "12345"
        device = Device(uuid=uuid, location_id="L1", description="some description")

        db.session.add(device)
        db.session.commit()

        response = client.get(f"/dhos/v1/device/{uuid}/jwt", headers={})
        assert response.status_code == 400

    def test_returns_400_when_json_body_has_extra_keys(
        self, client: FlaskClient
    ) -> None:
        uuid = "12345"
        device = Device(uuid=uuid, location_id="L1", description="some description")

        db.session.add(device)
        db.session.commit()

        response = client.get(
            f"/dhos/v1/device/{uuid}/jwt",
            json={"auth_code": "invalid-code", "extra": "key"},
        )
        assert response.status_code == 400

    def test_returns_403_auth_code_is_invalid(self, client: FlaskClient) -> None:
        uuid = "12345"
        device = Device(
            uuid=uuid,
            location_id="L1",
            description="some description",
            hashed_authorisation_code=b"12345",
            authorisation_code_salt="12345",
        )

        db.session.add(device)
        db.session.commit()

        response = client.get(
            f"/dhos/v1/device/{uuid}/jwt",
            headers={"x-authorisation-code": "invalid-code"},
        )
        assert response.status_code == 403

    @pytest.mark.usefixtures("mock_dhosredis")
    def test_passes(self, client: FlaskClient, app: Flask) -> None:

        uuid = "12345"
        auth_code = generate_secure_random_string(
            app.config["AUTHORISATION_CODE_LENGTH"]
        )
        auth_code_salt = generate_secure_random_string(app.config["SALT_LENGTH"])
        hashed_auth_code = hash_ascii_with_salt(auth_code, auth_code_salt)

        device = Device(
            uuid=uuid,
            location_id="L1",
            description="some description",
            hashed_authorisation_code=hashed_auth_code,
            authorisation_code_salt=auth_code_salt,
        )

        db.session.add(device)
        db.session.commit()

        response = client.get(
            f"/dhos/v1/device/{uuid}/jwt", headers={"x-authorisation-code": auth_code}
        )

        assert response.status_code == 200
        assert response.json is not None
        assert "jwt" in response.json

    @pytest.mark.usefixtures("mock_dhosredis")
    def test_returns_403_device_is_deactivated(
        self, client: FlaskClient, app: Flask
    ) -> None:
        uuid = "12345"
        auth_code = generate_secure_random_string(
            app.config["AUTHORISATION_CODE_LENGTH"]
        )
        auth_code_salt = generate_secure_random_string(app.config["SALT_LENGTH"])
        hashed_auth_code = hash_ascii_with_salt(auth_code, auth_code_salt)

        device = Device(
            uuid=uuid,
            location_id="L1",
            description="some description",
            hashed_authorisation_code=hashed_auth_code,
            authorisation_code_salt=auth_code_salt,
            active=False,
        )

        db.session.add(device)
        db.session.commit()

        response = client.get(
            f"/dhos/v1/device/{uuid}/jwt",
            headers={"x-authorisation-code": auth_code},
        )
        assert response.status_code == 403

from flask import Flask
from flask.testing import FlaskClient

from dhos_activation_auth_api.helpers.utils import generate_secure_random_string
from dhos_activation_auth_api.models.device import Device, db
from dhos_activation_auth_api.models.device_activation import DeviceActivation


class TestActivateDevice:
    def test_returns_400_when_device_type_unknown(self, client: FlaskClient) -> None:
        response = client.post("/dhos/v1/activation/anything?type=unknown_type")
        assert response.status_code == 400

    def test_returns_404_when_activation_code_does_not_exist(
        self, client: FlaskClient
    ) -> None:
        response = client.post("/dhos/v1/activation/nope?type=send_entry")
        assert response.status_code == 404

    def test_returns_404_when_activation_already_used(
        self, client: FlaskClient, app: Flask
    ) -> None:
        uuid = "12345"
        activation_code: str = generate_secure_random_string(
            app.config["AUTHORISATION_CODE_LENGTH"]
        )

        device = Device(
            uuid=uuid,
            location_id="L1",
            description="some description",
            hashed_authorisation_code=b"12345",
            authorisation_code_salt="SOMETHING",
        )
        activation = DeviceActivation(
            uuid="12345", device_id=uuid, code=activation_code, used=True
        )

        db.session.add(device)
        db.session.add(activation)
        db.session.commit()

        response = client.post(f"/dhos/v1/activation/{activation_code}?type=send_entry")
        assert response.status_code == 404

    def test_get_jwt_from_unactivated_device(
        self, client: FlaskClient, app: Flask
    ) -> None:
        uuid = "12345"
        activation_code = generate_secure_random_string(
            app.config["AUTHORISATION_CODE_LENGTH"]
        )

        device = Device(uuid=uuid, location_id="L1", description="some description")
        activation = DeviceActivation(uuid=uuid, device_id=uuid, code=activation_code)

        db.session.add(device)
        db.session.add(activation)
        db.session.commit()

        response = client.get(
            f"/dhos/v1/device/{uuid}/jwt", headers={"x-authorisation-code": "fake"}
        )

        assert response.status_code == 403

    def test_successful_device_activation_flow(
        self, client: FlaskClient, app: Flask
    ) -> None:

        uuid = "12345"
        activation_code = generate_secure_random_string(
            app.config["AUTHORISATION_CODE_LENGTH"]
        )

        device = Device(uuid=uuid, location_id="L1", description="some description")
        activation = DeviceActivation(
            uuid="12345", device_id=uuid, code=activation_code
        )

        db.session.add(device)
        db.session.add(activation)
        db.session.commit()

        response = client.post(f"/dhos/v1/activation/{activation_code}?type=send_entry")

        assert response.status_code == 200
        assert response.json is not None
        assert "authorisation_code" in response.json
        assert "device_id" in response.json

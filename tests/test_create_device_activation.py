from flask.testing import FlaskClient

from dhos_activation_auth_api.models.device import Device, db
from dhos_activation_auth_api.models.device_activation import DeviceActivation


class TestCreateDeviceActivation:
    def test_returns_404_when_device_does_not_exist(self, client: FlaskClient) -> None:
        response = client.post("/dhos/v1/nope/activation")
        assert response.status_code == 404

    def test_passes_with_new_activation(self, client: FlaskClient) -> None:
        uuid = "12345"
        device = Device(uuid=uuid, location_id="L1", description="")
        db.session.add(device)
        db.session.commit()
        response = client.post(
            f"/dhos/v1/device/{uuid}/activation",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_passes_with_existing_activation(self, client: FlaskClient) -> None:
        uuid = "12345"
        device = Device(uuid=uuid, location_id="L1", description="")
        db.session.add(device)
        db.session.commit()
        activation = DeviceActivation(uuid="bleughhh", device_id=uuid, code="demcodez")
        db.session.add(activation)
        db.session.commit()
        response = client.post(
            f"/dhos/v1/device/{uuid}/activation",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_static_activation(self, client: FlaskClient) -> None:
        uuid = "static_device_uuid_D5"
        device = Device(uuid=uuid, location_id="L1", description="")
        db.session.add(device)
        db.session.commit()
        response = client.post(
            f"/dhos/v1/device/{uuid}/activation",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["code"] == uuid[-1] * 9  # Should be static activation code

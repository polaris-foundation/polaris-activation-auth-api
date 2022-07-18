import pytest
from flask.testing import FlaskClient


@pytest.mark.usefixtures("app")
class TestUpdateDevice:
    def create_device(self, client: FlaskClient) -> str:
        response = client.post(
            "/dhos/v1/device",
            json={"location_id": "L1", "description": "a SEND entry device"},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["location_id"] == "L1"
        return response.json["uuid"]

    def test_update_device_location(self, client: FlaskClient) -> None:
        loc_uuid: str = self.create_device(client)
        response = client.patch(
            f"/dhos/v1/device/{loc_uuid}",
            json={"location_id": "L2"},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["location_id"] == "L2"

    def test_update_device_description(self, client: FlaskClient) -> None:
        loc_uuid: str = self.create_device(client)
        response = client.patch(
            f"/dhos/v1/device/{loc_uuid}",
            json={"description": "something descriptive"},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["description"] == "something descriptive"

    def test_update_device_id_and_description(self, client: FlaskClient) -> None:
        loc_uuid: str = self.create_device(client)
        response = client.patch(
            f"/dhos/v1/device/{loc_uuid}",
            json={"location_id": "L2", "description": "something descriptive"},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["location_id"] == "L2"
        assert response.json["description"] == "something descriptive"

    def test_fails_when_missing_json_body(self, client: FlaskClient) -> None:
        response = client.patch(
            "/dhos/v1/device/1234", json=None, headers={"Authorization": "Bearer TOKEN"}
        )
        assert response.status_code == 400

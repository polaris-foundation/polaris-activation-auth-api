import pytest
from flask.testing import FlaskClient


@pytest.mark.usefixtures("app")
class TestGetDevices:
    def create_devices(self, client: FlaskClient, count: int = 10) -> None:
        for i in range(count):
            location = "L1" if i % 2 else "L2"

            create_response = client.post(
                "/dhos/v1/device",
                json={"location_id": location, "description": f"{i}"},
                headers={"Authorization": "Bearer TOKEN"},
            )
            assert create_response.status_code == 200
            assert create_response.json is not None
            if i % 5 == 0:
                update_response = client.patch(
                    f"/dhos/v1/device/{create_response.json['uuid']}",
                    json={"active": False},
                    headers={"Authorization": "Bearer TOKEN"},
                )
                assert update_response.status_code == 200

    def test_returns_inactive_devices(self, client: FlaskClient) -> None:
        self.create_devices(client)
        response = client.get(
            "/dhos/v1/device?active=false", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json) == 2

    def test_returns_active_devices(self, client: FlaskClient) -> None:
        self.create_devices(client)
        response = client.get(
            "/dhos/v1/device?active=true", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json) == 8

    def test_returns_active_devices_implicitly(self, client: FlaskClient) -> None:
        self.create_devices(client)
        response = client.get(
            "/dhos/v1/device", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json) == 8

    def test_returns_devices_by_location(self, client: FlaskClient) -> None:
        self.create_devices(client)
        response = client.get(
            "/dhos/v1/device?location_id=L1", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json) == 4
        for d in response.json:
            assert d["location_id"] == "L1"

    def test_returns_devices_by_multiple_locations(self, client: FlaskClient) -> None:
        self.create_devices(client)
        response = client.get(
            "/dhos/v1/device?location_id=L1,L2",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json) == 8
        for d in response.json:
            assert d["location_id"] in ("L1", "L2")

    def test_fails_with_json_body(self, client: FlaskClient) -> None:
        response = client.get(
            "/dhos/v1/device",
            json={"some": "value"},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

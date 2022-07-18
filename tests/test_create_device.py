from flask.testing import FlaskClient


class TestCreateDevice:

    object_keys = ("uuid", "created", "modified", "location_id", "description")

    def test_passes(self, client: FlaskClient) -> None:
        response = client.post(
            "/dhos/v1/device",
            json={"location_id": "L1", "description": "a SEND entry device"},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        for key in self.object_keys:
            assert key in response.json

    def test_fails_when_missing_json_body(self, client: FlaskClient) -> None:
        response = client.post(
            "/dhos/v1/device", json=None, headers={"Authorization": "Bearer TOKEN"}
        )
        assert response.status_code == 400

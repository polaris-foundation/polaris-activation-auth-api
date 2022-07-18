from flask.testing import FlaskClient


class TestGetDevice:
    def test_returns_device(self, client: FlaskClient) -> None:
        post_response = client.post(
            "/dhos/v1/device",
            json={"location_id": "L1", "description": "here is a fun description"},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert post_response.status_code == 200
        assert post_response.json is not None
        device_uuid = post_response.json["uuid"]

        get_response = client.get(
            f"/dhos/v1/device/{device_uuid}", headers={"Authorization": "Bearer TOKEN"}
        )

        assert get_response.json is not None
        assert get_response.json["location_id"] == "L1"
        assert get_response.json["description"] == "here is a fun description"
        assert get_response.json["uuid"] == device_uuid

    def test_fails_to_return_device(self, client: FlaskClient) -> None:
        get_response = client.get(
            f"/dhos/v1/device/1234", headers={"Authorization": "Bearer TOKEN"}
        )
        assert get_response.status_code == 404

    def test_400_with_json_body(self, client: FlaskClient) -> None:
        get_response = client.get(
            f"/dhos/v1/device/1234",
            json={"some": "value"},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert get_response.status_code == 400

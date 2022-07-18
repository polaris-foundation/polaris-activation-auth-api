from datetime import date, datetime, timedelta
from typing import Dict

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_batteries_included.sqldb import db
from jose import jwt
from pytest_mock import MockFixture
from werkzeug.test import TestResponse

from dhos_activation_auth_api.blueprint_api import controller
from dhos_activation_auth_api.models.clinician import Clinician


@pytest.mark.usefixtures("app")
class TestClinicianJwt:
    def _create_clinician(self, client: FlaskClient, clinician: Dict) -> TestResponse:
        return client.post(
            "/dhos/v1/clinician",
            json=clinician,
            headers={"Authorization": "Bearer TOKEN"},
        )

    def _retrieve_clinician_jwt(
        self, client: FlaskClient, send_entry_identifier: str
    ) -> TestResponse:
        return client.get(
            f"/dhos/v1/clinician/jwt?send_entry_identifier={send_entry_identifier}",
            headers={"Authorization": "Bearer TOKEN"},
        )

    def test_create_clinician(
        self, client: FlaskClient, sample_clinician: Dict
    ) -> None:
        response = self._create_clinician(client, sample_clinician)
        assert response.status_code == 201
        assert response.json is None

    def test_create_clinician_with_extra_param(
        self, client: FlaskClient, sample_clinician: Dict
    ) -> None:
        clinician = {**sample_clinician, "something": "abcedf12345"}
        response = self._create_clinician(client, clinician)
        assert response.status_code == 400

    @pytest.mark.usefixtures("mock_retrieve_jwt_claims")
    def test_get_clinician_jwt_success(
        self,
        app: Flask,
        client: FlaskClient,
        sample_clinician: Dict,
        mocker: MockFixture,
        device_jwt_uuid: str,
    ) -> None:
        clinician = {**sample_clinician, "clinician_id": "ANEWID"}
        expected_scope = "read:thing1 write:thing2"
        controller.create_clinician(clinician)
        mocker.patch(
            "dhos_activation_auth_api.blueprint_api.audit.record_sendentry_login_success"
        )
        mocker.patch.object(
            controller, "get_send_entry_clinician_scope", return_value=expected_scope
        )

        resp = self._retrieve_clinician_jwt(
            client, sample_clinician["send_entry_identifier"]
        )
        assert resp.status_code == 200
        assert resp.json is not None
        decoded_jwt = jwt.decode(
            resp.json["jwt"],
            key="secret",
            algorithms=["HS512"],
            options={"verify_signature": False, "verify_aud": False},
        )

        assert decoded_jwt["scope"] == expected_scope
        assert "clinician_id" in decoded_jwt["metadata"]
        assert decoded_jwt["metadata"]["referring_device_id"] == device_jwt_uuid

        td = timedelta(days=app.config["JWT_EXPIRY_IN_SECONDS"])
        assert decoded_jwt["exp"] <= (datetime.utcnow() + td).timestamp()

    def test_403_when_creating_jwt_for_clinician_with_inactive_login(self) -> None:
        identifier = "some-identifier"
        obj = Clinician()
        obj.uuid = "this-is-a-uuid"
        obj.clinician_id = "some-clinician-id"
        obj.login_active = False
        obj.send_entry_identifier = identifier
        obj.products = []
        db.session.add(obj)
        db.session.commit()

        with pytest.raises(PermissionError):
            controller.create_clinician_jwt(identifier, "device_uuid")

    def test_403_when_creating_jwt_for_expired_clinician(self) -> None:
        identifier = "some-identifier"
        obj = Clinician()
        obj.uuid = "this-is-a-uuid"
        obj.clinician_id = "some-clinician-id"
        obj.login_active = True
        obj.send_entry_identifier = identifier
        obj.contract_expiry_eod_date_ = date.today() - timedelta(days=1)
        obj.products = []
        db.session.add(obj)
        db.session.commit()

        with pytest.raises(PermissionError):
            controller.create_clinician_jwt(identifier, "device_uuid")

        obj = Clinician.query.filter_by(send_entry_identifier=identifier).first()

        assert obj is not None
        assert obj.login_active is False

    @pytest.mark.usefixtures("mock_retrieve_jwt_claims")
    def test_get_clinician_jwt_nonexistent_identifier(
        self,
        mocker: MockFixture,
        client: FlaskClient,
        sample_clinician: Dict,
        device_jwt_uuid: str,
    ) -> None:
        mocker.patch(
            "dhos_activation_auth_api.blueprint_api.audit.record_sendentry_login_failure"
        )
        response = self._retrieve_clinician_jwt(
            client,
            sample_clinician["send_entry_identifier"],
        )
        assert response.status_code == 404

    def test_get_clinician_jwt_no_identifier(self, client: FlaskClient) -> None:
        response = client.get(
            f"/dhos/v1/clinician/jwt", headers={"Authorization": "Bearer TOKEN"}
        )
        assert response.status_code == 400

    def test_get_clinician_jwt_no_auth(self, client: FlaskClient) -> None:
        response = client.get(f"/dhos/v1/clinician/jwt?send_entry_identifier=123")
        assert response.status_code == 401

    @pytest.mark.usefixtures("mock_dhosredis")
    def test_update_clinician(
        self, sample_clinician: Dict, sample_clinician_update: Dict, client: FlaskClient
    ) -> None:

        response = self._create_clinician(clinician=sample_clinician, client=client)
        assert response.status_code == 201

        sample_clinician_update["products"].append("SEND")

        response = client.patch(
            f"/dhos/v1/clinician/{sample_clinician['clinician_id']}",
            json=sample_clinician_update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

        clinician_jwt = controller.create_clinician_jwt(
            sample_clinician_update["send_entry_identifier"], device_uuid="device_uuid"
        )
        assert "jwt" in clinician_jwt

    def test_403_when_creating_jwt_for_clinician_without_group(self) -> None:
        identifier = "some-identifier-1"

        obj = Clinician()
        obj.uuid = "this-is-a-uuid-1"
        obj.clinician_id = "some-clinician-id-1"
        obj.login_active = True
        obj.send_entry_identifier = identifier
        obj.products = []
        db.session.add(obj)
        db.session.commit()

        with pytest.raises(PermissionError):
            controller.create_clinician_jwt(identifier, "device_uuid")

    def test_send_admin_does_not_have_send_entry_access(
        self, sample_clinician: Dict, client: FlaskClient
    ) -> None:
        sample_clinician["groups"] = ["send administrator"]
        sample_clinician["send_entry_identifier"] = "007"
        response = self._create_clinician(clinician=sample_clinician, client=client)
        assert response.status_code == 201

        obj: Clinician = Clinician.query.filter_by(
            send_entry_identifier=sample_clinician["send_entry_identifier"]
        ).first()
        is_allowed = controller.clinician_has_send_entry_access(obj)
        assert is_allowed is False

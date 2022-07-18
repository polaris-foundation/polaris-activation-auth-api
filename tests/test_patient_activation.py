from typing import Dict, Optional

import pytest
from flask import Flask, current_app
from flask.testing import FlaskClient
from jose import jwt
from pytest_mock import MockFixture
from werkzeug.test import TestResponse

from dhos_activation_auth_api.blueprint_api import controller
from dhos_activation_auth_api.helpers.utils import hash_ascii_with_salt
from dhos_activation_auth_api.models.patient_activation import PatientActivation


class TestCreatePatientActivation:
    def _create_activation(
        self, client: FlaskClient, patient_id: str = "12345"
    ) -> TestResponse:
        response = client.post(
            f"/dhos/v1/patient/{patient_id}/activation",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        return response

    def _generate_jwt(
        self,
        client: FlaskClient,
        patient_id: str,
        authorisation_code: str,
    ) -> TestResponse:
        return client.get(
            f"/dhos/v1/patient/{patient_id}/jwt",
            headers={"x-authorisation-code": authorisation_code},
        )

    def _create_and_return_activation(
        self, client: FlaskClient, patient_id: str
    ) -> Dict:
        response = self._create_activation(client, patient_id)
        assert response.json is not None
        otp = response.json.get("otp", None)
        assert otp is not None

        activation_code = response.json.get("activation_code", None)
        assert activation_code is not None

        # Cheat and find the activation by activation code
        activation: Optional[PatientActivation] = PatientActivation.query.filter_by(
            code=activation_code, used=False
        ).first()
        assert activation is not None

        return {"otp": otp, "activation_code": activation_code}

    def _generate_authorisation_code(self, client: FlaskClient, patient_id: str) -> str:
        activation = self._create_and_return_activation(client, patient_id)
        response = client.post(
            f"/dhos/v1/activation/{activation['activation_code']}",
            json={"otp": activation["otp"]},
        )
        assert response.status_code == 200
        assert response.json is not None
        authorisation_code = response.json.get("authorisation_code", None)
        assert authorisation_code is not None
        return authorisation_code

    def test_create_activation(self, client: FlaskClient) -> None:
        patient_id = "abcedf12345"
        response = self._create_activation(client, patient_id)
        assert response.json is not None
        assert response.json["otp"] is not None
        assert response.json["activation_code"] is not None

    @pytest.mark.usefixtures("mock_dhosredis")
    def test_create_on_existing_activation(self, client: FlaskClient) -> None:
        patient_id = "abcedf12345"
        response = self._create_activation(client, patient_id)
        assert response.json is not None
        activation_code = response.json["activation_code"]
        response2 = self._create_activation(client, patient_id)
        assert response2.json is not None
        assert activation_code == response2.json["activation_code"]

    @pytest.mark.usefixtures("mock_dhosredis")
    def test_create_on_completed_activation(self, client: FlaskClient) -> None:
        patient_id = "abcedf12345"

        # Generate auth code
        authorisation_code = self._generate_authorisation_code(client, patient_id)

        # Use auth code
        response = self._generate_jwt(client, patient_id, authorisation_code)
        assert response.status_code == 200

        # Create another auth code
        authorisation_code2 = self._generate_authorisation_code(client, patient_id)
        assert authorisation_code != authorisation_code2

        # Successfully use the new authorisation code
        response2 = self._generate_jwt(client, patient_id, authorisation_code2)
        assert response2.status_code == 200

        # The original authorisation code should now fail
        response3 = self._generate_jwt(client, patient_id, authorisation_code)
        assert response3.status_code == 404

    def test_update_activation(self, client: FlaskClient) -> None:
        patient_id = "abcedf12345"

        auth_code = self._generate_authorisation_code(client, patient_id)

        # Check the activation is in the database
        used_activation: Optional[
            PatientActivation
        ] = PatientActivation.query.filter_by(patient_id=patient_id, used=True).first()
        assert used_activation is not None

        hashed_authorisation_code = used_activation.patient.hashed_authorisation_code
        authorisation_code_salt = used_activation.patient.authorisation_code_salt

        assert (
            hash_ascii_with_salt(auth_code, authorisation_code_salt)
            == hashed_authorisation_code
        )

    def test_update_nonexistent_activation(self, client: FlaskClient) -> None:
        response = client.post(f"/dhos/v1/activation/{123}", json={"otp": "456"})
        assert response.status_code == 404

    def test_eleventh_try_404(self, client: FlaskClient) -> None:
        patient_id = "abcedf12345"
        activation = self._create_and_return_activation(client, patient_id)
        for i in range(1, 11):
            response = client.post(
                f"/dhos/v1/activation/{activation['activation_code']}",
                json={"otp": "456"},
            )
            assert response.status_code == 404

        response = client.post(
            f"/dhos/v1/activation/{activation['activation_code']}",
            json={"otp": activation["otp"]},
        )
        assert response.status_code == 404

    def test_create_jwt(self, client: FlaskClient, mocker: MockFixture) -> None:
        patient_id = "abcedf12345"
        authorisation_code = self._generate_authorisation_code(client, patient_id)
        expected_scope = "read:thing1 write:thing2"

        mocker.patch.object(
            controller, "get_gdm_patient_scope", return_value=expected_scope
        )
        jwt_response = self._generate_jwt(client, patient_id, authorisation_code)
        assert jwt_response.json is not None
        patient_jwt = jwt_response.json["jwt"]

        hs_key = current_app.config.get("HS_KEY", None)
        audience = current_app.config.get("PROXY_URL", None)

        assert hs_key is not None
        assert audience is not None

        audience += "/"

        decoded = jwt.decode(patient_jwt, hs_key, algorithms="HS512", audience=audience)
        assert decoded["metadata"]["patient_id"] == patient_id
        assert decoded["scope"] == expected_scope

    def test_get_patient_jwt_without_header(self, client: FlaskClient) -> None:
        response = client.get(
            f"/dhos/v1/patient/123/jwt",
        )
        assert response.status_code == 400

    def test_get_patient_jwt_unknown_patient(self, client: FlaskClient) -> None:
        response = self._generate_jwt(
            client=client, patient_id="unknown_patient", authorisation_code="something"
        )
        assert response.status_code == 404

    def test_no_installations_on_wrong_patient_id(self, client: FlaskClient) -> None:
        patient_id = "67676"
        response = client.get(
            f"/dhos/v1/patient/{patient_id}/activation",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json == []

    @pytest.mark.usefixtures("mock_dhosredis")
    def test_activation_returned(self, client: FlaskClient) -> None:
        patient_id = "fff12345"
        authorisation_code = self._generate_authorisation_code(client, patient_id)
        self._generate_jwt(client, patient_id, authorisation_code)

        response = client.get(
            f"/dhos/v1/patient/{patient_id}/activation",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.json is not None
        assert "activation_completed" in response.json[0]

    def test_static_activation(self, app: Flask, client: FlaskClient) -> None:
        patient_id = "static_patient_uuid_1"
        response = self._create_activation(client, patient_id)
        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("otp", None) == "1111"
        assert response.json.get("activation_code", None) == "1"

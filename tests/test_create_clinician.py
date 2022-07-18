from typing import Dict

import pytest
from werkzeug import Client

from dhos_activation_auth_api.blueprint_api import controller
from dhos_activation_auth_api.models.clinician import Clinician


@pytest.mark.usefixtures("app")
class TestCreateClinician:
    @pytest.fixture
    def clinician(self) -> Dict:
        return {
            "uuid": "this-is-pointless",
            "clinician_id": "123-456-789",
            "login_active": True,
            "send_entry_identifier": "321-654-987",
            "products": [],
            "groups": [],
            "contract_expiry_eod_date": None,
        }

    def test_create_send_clinician(self, client: Client, clinician: Dict) -> None:
        # Arrange
        clinician["contract_expiry_eod_date"] = "2019-01-01"

        # Act
        response = client.post(
            "dhos/v1/clinician",
            json=clinician,
            headers={"Authorization": "Bearer TOKEN"},
        )

        # Assert
        assert response.status_code == 201
        obj = Clinician.query.filter_by(clinician_id=clinician["clinician_id"]).first()
        assert obj is not None
        assert obj.clinician_id == clinician["clinician_id"]
        assert obj.send_entry_identifier == clinician["send_entry_identifier"]
        assert obj.contract_expiry_eod_date == "2019-01-01"

    def test_create_gdm_clinician(self, client: Client, clinician: Dict) -> None:
        # Arrange
        clinician["send_entry_identifier"] = None

        # Act
        response = client.post(
            "dhos/v1/clinician",
            json=clinician,
            headers={"Authorization": "Bearer TOKEN"},
        )

        # Assert
        assert response.status_code == 201
        obj = Clinician.query.filter_by(clinician_id=clinician["clinician_id"]).first()
        assert obj is not None
        assert obj.clinician_id == clinician["clinician_id"]
        assert obj.send_entry_identifier is None

    def test_patch_send_clinician(self, client: Client, clinician: Dict) -> None:
        # Arrange
        controller.create_clinician(clinician)
        send_entry_identifier = "123"
        contract_expiry_eod_date = "2018-01-01"
        payload = {
            "products": [],
            "groups": [],
            "send_entry_identifier": send_entry_identifier,
            "contract_expiry_eod_date": contract_expiry_eod_date,
        }

        # Act
        response = client.patch(
            f"dhos/v1/clinician/{clinician['clinician_id']}",
            json=payload,
            headers={"Authorization": "Bearer TOKEN"},
        )

        # Assert
        assert response.status_code == 200
        obj = Clinician.query.filter_by(clinician_id=clinician["clinician_id"]).first()
        assert obj is not None
        assert obj.clinician_id == clinician["clinician_id"]
        assert obj.send_entry_identifier == "123"
        assert obj.contract_expiry_eod_date == "2018-01-01"

    def test_patch_gdm_clinician(self, client: Client, clinician: Dict) -> None:
        # Arrange
        controller.create_clinician(clinician)
        payload = {
            "products": [],
            "groups": [],
            "login_active": False,
            "send_entry_identifier": None,
            "contract_expiry_eod_date": None,
        }

        # Act
        response = client.patch(
            f"dhos/v1/clinician/{clinician['clinician_id']}",
            json=payload,
            headers={"Authorization": "Bearer TOKEN"},
        )

        # Assert
        assert response.status_code == 200
        obj = Clinician.query.filter_by(clinician_id=clinician["clinician_id"]).first()
        assert obj is not None
        assert obj.clinician_id == clinician["clinician_id"]
        assert obj.login_active is False
        assert obj.send_entry_identifier is None
        assert obj.contract_expiry_eod_date is None

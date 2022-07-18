import uuid
from unittest.mock import Mock

import kombu_batteries_included
import pytest
from pytest_mock import MockFixture

from dhos_activation_auth_api.blueprint_api import audit


class TestAudit:
    @pytest.fixture
    def mock_publish(self, mocker: MockFixture) -> Mock:
        return mocker.patch.object(kombu_batteries_included, "publish_message")

    def test_record_sendentry_login_failure(self, mock_publish: Mock) -> None:
        device_id = str(uuid.uuid4())
        reason = "something bad has happened"
        send_entry_identifier = "C3PO"
        clinician_id = str(uuid.uuid4())
        expected = {
            "event_type": "SEND entry login failure",
            "event_data": {
                "reason": reason,
                "device_id": device_id,
                "send_entry_identifier": send_entry_identifier,
                "clinician_id": clinician_id,
            },
        }
        audit.record_sendentry_login_failure(
            device_id=device_id,
            reason=reason,
            send_entry_identifier=send_entry_identifier,
            clinician_id=clinician_id,
        )
        mock_publish.assert_called_with(routing_key="dhos.34837004", body=expected)

    def test_record_sendentry_login_success(self, mock_publish: Mock) -> None:
        device_id = str(uuid.uuid4())
        clinician_id = str(uuid.uuid4())
        send_entry_identifier = "R2D2"
        expected = {
            "event_type": "SEND entry login success",
            "event_data": {
                "device_id": device_id,
                "clinician_id": clinician_id,
                "send_entry_identifier": send_entry_identifier,
            },
        }
        audit.record_sendentry_login_success(
            device_id=device_id,
            clinician_id=clinician_id,
            send_entry_identifier=send_entry_identifier,
        )
        mock_publish.assert_called_with(routing_key="dhos.34837004", body=expected)

    def test_record_sendentry_device_auth_failure(self, mock_publish: Mock) -> None:
        device_id = str(uuid.uuid4())
        reason = "Alien invasion"
        expected = {
            "event_type": "SEND entry device auth failed",
            "event_data": {"device_id": device_id, "reason": reason},
        }
        audit.record_sendentry_device_auth_failure(device_id=device_id, reason=reason)
        mock_publish.assert_called_with(routing_key="dhos.34837004", body=expected)

    def test_record_sendentry_device_auth_success(self, mock_publish: Mock) -> None:
        device_id = str(uuid.uuid4())
        expected = {
            "event_type": "SEND entry device auth success",
            "event_data": {"device_id": device_id},
        }
        audit.record_sendentry_device_auth_success(device_id=device_id)
        mock_publish.assert_called_with(routing_key="dhos.34837004", body=expected)

    def test_record_sendentry_device_update(self, mock_publish: Mock) -> None:
        device_id = str(uuid.uuid4())
        clinician_id = str(uuid.uuid4())
        updated_fields = {"one": 1, "two": 2, "three": 3}
        expected = {
            "event_type": "SEND entry device update",
            "event_data": {
                "device_id": device_id,
                "clinician_id": clinician_id,
                "updated_fields": updated_fields,
            },
        }
        audit.record_sendentry_device_update(
            device_id=device_id,
            clinician_id=clinician_id,
            updated_fields=updated_fields,
        )
        mock_publish.assert_called_with(routing_key="dhos.34837004", body=expected)

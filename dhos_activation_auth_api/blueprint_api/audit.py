from typing import Any, Dict, Optional

import kombu_batteries_included


def record_sendentry_login_failure(
    device_id: str,
    reason: str,
    send_entry_identifier: str,
    clinician_id: Optional[str] = None,
) -> None:
    event_data = {
        "device_id": device_id,
        "reason": reason,
        "send_entry_identifier": send_entry_identifier,
    }
    if clinician_id is not None:
        event_data["clinician_id"] = clinician_id
    audit = {
        "event_type": "SEND entry login failure",
        "event_data": event_data,
    }
    kombu_batteries_included.publish_message(routing_key="dhos.34837004", body=audit)


def record_sendentry_login_success(
    device_id: str,
    clinician_id: str,
    send_entry_identifier: Optional[str] = None,
) -> None:
    event_data = {"device_id": device_id, "clinician_id": clinician_id}
    if send_entry_identifier:
        event_data["send_entry_identifier"] = send_entry_identifier
    audit = {
        "event_type": "SEND entry login success",
        "event_data": event_data,
    }
    kombu_batteries_included.publish_message(routing_key="dhos.34837004", body=audit)


def record_sendentry_device_auth_failure(device_id: str, reason: str) -> None:
    event_data = {"device_id": device_id, "reason": reason}
    audit = {
        "event_type": "SEND entry device auth failed",
        "event_data": event_data,
    }
    kombu_batteries_included.publish_message(routing_key="dhos.34837004", body=audit)


def record_sendentry_device_auth_success(device_id: str) -> None:
    event_data = {"device_id": device_id}
    audit = {
        "event_type": "SEND entry device auth success",
        "event_data": event_data,
    }
    kombu_batteries_included.publish_message(routing_key="dhos.34837004", body=audit)


def record_sendentry_device_update(
    device_id: str, clinician_id: str, updated_fields: Dict[str, Any]
) -> None:
    audit = {
        "event_type": "SEND entry device update",
        "event_data": {
            "device_id": device_id,
            "clinician_id": clinician_id,
            "updated_fields": updated_fields,
        },
    }
    kombu_batteries_included.publish_message(routing_key="dhos.34837004", body=audit)

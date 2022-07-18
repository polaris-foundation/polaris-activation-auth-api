import random
import string
import uuid
from typing import Dict

from behave import given, step, then
from behave.runner import Context
from clients import activation_auth_api_client as client
from jose import jwt as jose_jwt
from she_logging import logger


@step("I deactivate the clinician")
def deactivate_clinician(context: Context) -> None:
    # we need to set all the data or else the missing values will be cleared...
    clinician_details = context.clinician_details
    del clinician_details["clinician_id"]  # but we can't update the clinician_id
    clinician_details["login_active"] = False

    response = client.patch_clinician(
        clinician_details=clinician_details,
        clinician_id=context.clinician_uuid,
        jwt=context.system_jwt,
    )
    response.raise_for_status()


@given("I am a known clinician")
def create_clinician(context: Context) -> None:
    context.clinician_uuid = str(uuid.uuid4())
    logger.debug("clinician uuid: %s", context.clinician_uuid)
    context.clinician_send_entry_identifier = "".join(
        random.choice(string.digits) for _ in range(6)
    )
    clinician_details = {
        "clinician_id": context.clinician_uuid,
        "groups": ["SEND Superclinician"],
        "login_active": True,
        "products": ["SEND"],
        "send_entry_identifier": context.clinician_send_entry_identifier,
    }
    context.clinician_details = clinician_details
    response = client.post_clinician(
        clinician_details=clinician_details,
        jwt=context.system_jwt,
    )
    assert response.status_code == 201


@then("I {can_or_can_not} use the device JWT to generate a valid clinician JWT")
def generate_clinician_jwt(context: Context, can_or_can_not: str) -> None:
    response = client.get_clinician_jwt(
        context.clinician_send_entry_identifier, context.device_jwt
    )
    if can_or_can_not == "can":
        assert response.status_code == 200
        claims: Dict = jose_jwt.get_unverified_claims(response.json()["jwt"])
        assert claims["metadata"]["clinician_id"] == context.clinician_uuid
        assert claims["metadata"]["referring_device_id"] == context.device_uuid
    else:
        assert response.status_code == 403

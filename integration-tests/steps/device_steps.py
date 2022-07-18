import uuid
from typing import Dict

from behave import given, step, then
from behave.runner import Context
from clients import activation_auth_api_client as client
from jose import jwt as jose_jwt


@given("a device exists")
def create_device(context: Context) -> None:
    response = client.post_device(
        device_details={
            "description": "Integration test SEND Tablet",
            "location_id": str(uuid.uuid4()),
        },
        device_type="send_entry",
        jwt=context.system_jwt,
    )
    assert response.status_code == 200
    context.device_uuid = response.json()["uuid"]


@step("I deactivate the device")
def deactivate_device(context: Context) -> None:
    response = client.patch_device(
        device_details={
            "active": False,
        },
        device_uuid=context.device_uuid,
        jwt=context.system_jwt,
    )
    response.raise_for_status()


@step("I update the device")
def update_device(context: Context) -> None:
    updated_device_body = {
        "description": "Testing",
        "location_id": str(uuid.uuid4()),
        "active": False,
    }
    response = client.patch_device(
        device_details=updated_device_body,
        device_uuid=context.device_uuid,
        jwt=context.system_jwt,
    )
    response.raise_for_status()
    context.updated_device_body = updated_device_body


@step("I can get the device details")
def get_device_details(context: Context) -> None:
    response = client.get_device(
        device_uuid=context.device_uuid,
        jwt=context.system_jwt,
    )
    response.raise_for_status()
    context.updated_device_response = response


@step("I see the device details have been updated")
def assert_device_updated(context: Context) -> None:
    response_body: dict = context.updated_device_response.json()
    for key in context.updated_device_body:
        assert context.updated_device_body[key] == response_body[key]


@step("I request a device activation code")
def request_device_activation(context: Context) -> None:
    response = client.post_device_activation(
        device_uuid=context.device_uuid,
        jwt=context.system_jwt,
    )
    assert response.status_code == 200
    context.post_device_activation_response = response


@step("I validate the device activation using the code")
def validate_device_activation(context: Context) -> None:
    activation_code = context.post_device_activation_response.json()["code"]
    response = client.validate_device_activation(activation_code)
    context.validate_device_activation_response = response


@step("I receive a device authorisation code")
def validate_device_authorisation_code(context: Context) -> None:
    assert context.validate_device_activation_response.status_code == 200
    response_body: Dict = context.validate_device_activation_response.json()
    authorisation_code: str = response_body["authorisation_code"]
    assert isinstance(authorisation_code, str)
    assert len(authorisation_code) > 2


@then("I {can_or_can_not} use the code to generate a valid device JWT")
def generate_device_jwt(context: Context, can_or_can_not: str) -> None:
    assert can_or_can_not in ["can", "can not"]
    authorisation_code = context.validate_device_activation_response.json()[
        "authorisation_code"
    ]
    response = client.get_device_jwt(context.device_uuid, authorisation_code)

    if can_or_can_not == "can":
        assert response.status_code == 200
        context.device_jwt = response.json()["jwt"]
        claims: Dict = jose_jwt.get_unverified_claims(context.device_jwt)
        assert claims["metadata"]["device_id"] == context.device_uuid
    else:
        assert response.status_code == 403

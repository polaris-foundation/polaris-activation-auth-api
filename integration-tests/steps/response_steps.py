import re
from datetime import datetime, timedelta
from typing import Dict

from behave import then
from behave.runner import Context


@then("a patient activation code is returned")
def validate_patient_activation_response(context: Context) -> None:
    assert context.post_patient_activation_response.status_code == 200

    response_body: Dict = context.post_patient_activation_response.json()
    assert re.match(re.compile("^[a-zA-Z0-9_]{4}"), response_body["otp"]) is not None
    assert response_body["activation_code"] is not None
    expected_datetime = (datetime.now() + timedelta(days=5)).strftime(
        "%Y-%m-%d"
    ) + "T23:59:59.000"
    assert response_body["expires_at"] == expected_datetime


@then("I receive a patient authorisation code")
def validate_patient_authorisation_code(context: Context) -> None:
    assert context.validate_patient_activation_response.status_code == 200
    response_body: Dict = context.validate_patient_activation_response.json()
    authorisation_code: str = response_body["authorisation_code"]
    assert isinstance(authorisation_code, str)
    assert len(authorisation_code) > 2

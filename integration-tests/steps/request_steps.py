from behave import then, when
from behave.runner import Context
from clients import activation_auth_api_client as client


@when("I request a patient activation code")
def request_patient_activation(context: Context) -> None:
    response = client.post_patient_activation(
        patient_uuid=context.patient_uuid,
        jwt=context.system_jwt,
    )
    assert response.status_code == 200
    context.post_patient_activation_response = response


@when("I validate the patient activation using the code")
def validate_patient_activation(context: Context) -> None:
    activation_code = context.post_patient_activation_response.json()["activation_code"]
    otp: str = context.post_patient_activation_response.json()["otp"]
    response = client.validate_patient_activation(activation_code, otp)
    context.validate_patient_activation_response = response


@then("I can use the code to generate a valid patient JWT")
def generate_patient_jwt(context: Context) -> None:
    authorisation_code = context.validate_patient_activation_response.json()[
        "authorisation_code"
    ]
    response = client.get_patient_jwt(context.patient_uuid, authorisation_code)
    assert response.status_code == 200
    assert response.json()["jwt"].startswith("ey")

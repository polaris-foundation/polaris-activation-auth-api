import uuid

from behave import given
from behave.runner import Context
from helpers import security


@given("a patient record exists")
def generate_patient(context: Context) -> None:
    context.patient_uuid = str(uuid.uuid4())


@given("I have a valid JWT")
def get_system_jwt(context: Context) -> None:
    if not hasattr(context, "system_jwt"):
        context.system_jwt = security.generate_system_jwt()

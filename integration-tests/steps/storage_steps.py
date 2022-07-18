from behave import then
from behave.runner import Context
from clients.storage_client import patient_has_activation_record


@then("the patient activation is stored")
def assert_patient_activation_is_stored(context: Context) -> None:
    assert patient_has_activation_record(
        context=context, patient_uuid=context.patient_uuid
    )

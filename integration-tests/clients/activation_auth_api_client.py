from typing import Dict

import requests
from environs import Env
from requests import Response


def _get_base_url() -> str:
    return Env().str(
        "DHOS_ACTIVATION_AUTH_BASE_URL", "http://dhos-activation-auth-api:5000"
    )


def post_patient_activation(patient_uuid: str, jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/patient/{patient_uuid}/activation",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )


def validate_patient_activation(activation_code: str, otp: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/activation/{activation_code}",
        json={"otp": otp},
        timeout=15,
    )


def get_patient_jwt(patient_uuid: str, authorisation_code: str) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/patient/{patient_uuid}/jwt",
        headers={"x-authorisation-code": authorisation_code},
        timeout=15,
    )


def get_device(device_uuid: str, jwt: str) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/device/{device_uuid}",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )


def post_device(device_type: str, device_details: Dict, jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/device",
        headers={"Authorization": f"Bearer {jwt}"},
        params={"type": device_type},
        json=device_details,
        timeout=15,
    )


def patch_device(device_uuid: str, device_details: Dict, jwt: str) -> Response:
    return requests.patch(
        f"{_get_base_url()}/dhos/v1/device/{device_uuid}",
        headers={"Authorization": f"Bearer {jwt}"},
        json=device_details,
        timeout=15,
    )


def post_clinician(clinician_details: Dict, jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/clinician",
        headers={"Authorization": f"Bearer {jwt}"},
        json=clinician_details,
        timeout=15,
    )


def patch_clinician(clinician_id: str, clinician_details: Dict, jwt: str) -> Response:
    return requests.patch(
        f"{_get_base_url()}/dhos/v1/clinician/{clinician_id}",
        headers={"Authorization": f"Bearer {jwt}"},
        json=clinician_details,
        timeout=15,
    )


def post_device_activation(device_uuid: str, jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/device/{device_uuid}/activation",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )


def validate_device_activation(activation_code: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/activation/{activation_code}",
        params={"type": "send_entry"},
        timeout=15,
    )


def get_device_jwt(device_uuid: str, authorisation_code: str) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/device/{device_uuid}/jwt",
        headers={"x-authorisation-code": authorisation_code},
        timeout=15,
    )


def get_clinician_jwt(send_entry_identifier: str, device_jwt: str) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/clinician/jwt",
        headers={"Authorization": f"Bearer {device_jwt}"},
        params={"send_entry_identifier": send_entry_identifier},
        timeout=15,
    )

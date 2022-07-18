import string
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple, Union

import Cryptodome.Random.random as crr
from Cryptodome.Protocol.KDF import scrypt
from flask_batteries_included.config import is_production_environment

from dhos_activation_auth_api.models.device_activation import DeviceActivation
from dhos_activation_auth_api.models.patient_activation import PatientActivation

random_choices: str = string.ascii_uppercase + string.digits
not_human_readable_choices: List[str] = ["O", "0", "L", "1", "I"]


def _activation_expired(modified: datetime, number_of_days: int) -> bool:
    expiry_time: datetime = calculate_end_of_day_expiry(modified, number_of_days)
    now = datetime.utcnow()
    return now > expiry_time


def generate_secure_random_string(length: int = 10) -> str:
    if length < 3:
        raise ValueError("Cannot generate a secure random string of length < 3")

    letters: List[Any] = [crr.choice(random_choices) for _ in range(length)]
    return "".join(letters)


def generate_secure_human_readable_string(length: int = 4) -> str:
    if length < 3:
        raise ValueError("Cannot generate a secure random string of length < 3")

    safe_choices = set(random_choices) - set(not_human_readable_choices)

    letters: List[Any] = [crr.choice(list(safe_choices)) for _ in range(length)]
    return "".join(letters)


def generate_secure_numeric_string(length: int = 4) -> str:
    if length < 3:
        raise ValueError("Cannot generate a secure random string of length < 3")

    letters: List[Any] = [crr.choice(list(string.digits)) for _ in range(length)]
    return "".join(letters)


def hash_ascii_with_salt(
    ascii_string: str, salt: str
) -> Union[bytes, Tuple[bytes, ...]]:
    code_bytes: Any = bytes(ascii_string, "ascii")
    salt_bytes: Any = bytes(salt, "ascii")
    return scrypt(code_bytes, salt_bytes, 256, 16384, 8, 1)


def generate_seconds_from_now_expiry(exp_time_in_seconds: int) -> datetime:
    td = timedelta(seconds=exp_time_in_seconds)
    now = datetime.utcnow()
    return now + td


def calculate_end_of_day_expiry(
    from_datetime: datetime, number_of_days: int
) -> datetime:
    """
    Creates a datetime that is a certain number of days from `from_datetime`,
    pushed out to the end of that day.
    """
    td = timedelta(days=number_of_days)
    expiry_datetime = from_datetime + td
    return expiry_datetime.replace(hour=23, minute=59, second=59, microsecond=0)


def check_patient_activation_valid(
    activation: Optional[PatientActivation], activation_expired_end_of_nth_day: int
) -> bool:
    """
    Checks whether a patient activation is valid. Rules to an invalid patient activation:
    1) it can't find the activation in the database
    2) it can find the activation, but it's expired, and it's in production
    3) it can find the activation, but it's expired, and patient ID isn't static, and it's in nonproduction
    """
    if activation is None:
        return False

    if not _activation_expired(activation.modified, activation_expired_end_of_nth_day):
        return True

    if is_production_environment():
        return False

    if is_static_patient_id(activation.patient.patient_id):
        return True

    return False


def check_device_activation_valid(
    activation: Optional[DeviceActivation], activation_expired_end_of_nth_day: int
) -> bool:
    """
    Checks whether a device activation is valid. Rules to an invalid device activation:
    1) it can't find the activation in the database
    2) it can find the activation, but it's expired, and it's in production
    3) it can find the activation, but it's expired, and device ID isn't static, and it's in nonproduction
    """
    if activation is None:
        return False

    if not _activation_expired(activation.modified, activation_expired_end_of_nth_day):
        return True

    if is_production_environment():
        return False

    if is_static_device_id(activation.device_id):
        return True

    return False


def is_static_patient_id(patient_id: str) -> bool:
    """
    Static patients have 'UUIDs' in the form static_patient_uuid_1 (with numbers 1-9).
    """
    return patient_id in [f"static_patient_uuid_{i}" for i in range(1, 10)]


def is_static_device_id(device_id: str) -> bool:
    """
    Static devices have 'UUIDs' in the form static_device_uuid_D1 (with numbers 1-9).
    """
    return device_id in [f"static_device_uuid_D{i}" for i in range(1, 10)]

from typing import Optional

import dhosredis
from flask import current_app as app
from flask_batteries_included.config import is_production_environment
from flask_batteries_included.helpers.error_handler import ServiceUnavailableException
from she_logging import logger


def get_gdm_patient_scope() -> str:
    return _get_scope(
        cache_key="CACHED_GDM_PATIENT_SCOPE",
        group_name="GDM Patient",
        fallback_scope=app.config["MOCK_GDM_PATIENT_SCOPE"],
    )


def get_send_entry_clinician_scope() -> str:
    return _get_scope(
        cache_key="CACHED_SEND_ENTRY_CLINICIAN_SCOPE",
        group_name="SEND Entry Clinician",
        fallback_scope=app.config["MOCK_SEND_ENTRY_CLINICIAN_SCOPE"],
    )


def get_send_entry_device_scope() -> str:
    return _get_scope(
        cache_key="CACHED_SEND_ENTRY_DEVICE_SCOPE",
        group_name="SEND Entry Device",
        fallback_scope=app.config["MOCK_SEND_ENTRY_DEVICE_SCOPE"],
    )


def _get_scope(cache_key: str, group_name: str, fallback_scope: str) -> str:
    scope: Optional[str] = dhosredis.get_value(key=cache_key, default=None)
    if scope is None:
        if is_production_environment():
            raise ServiceUnavailableException(
                f"Could not retrieve {group_name} from redis"
            )
        scope = fallback_scope
        logger.warning(
            "Could not retrieve scope for %s from redis, falling back to mock",
            group_name,
        )
    return scope

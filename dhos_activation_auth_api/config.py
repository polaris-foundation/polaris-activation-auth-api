from typing import Optional

from environs import Env
from flask import Flask


class Configuration:
    env = Env()
    OTP_LENGTH: int = env.int("OTP_LENGTH", 4)
    SEND_ENTRY_ACTIVATION_CODE_LENGTH: int = env.int(
        "SEND_ENTRY_ACTIVATION_CODE_LENGTH", 9
    )
    ACTIVATION_EXPIRY_END_OF_NTH_DAY: int = env.int(
        "ACTIVATION_EXPIRY_END_OF_NTH_DAY", 5
    )
    AUTHORISATION_CODE_LENGTH: int = env.int("AUTHORISATION_CODE_LENGTH", 30)
    SALT_LENGTH: int = env.int("SALT_LENGTH", 30)
    JWT_EXPIRY_IN_SECONDS: int = env.int("JWT_EXPIRY_IN_SECONDS", 900)
    SEND_ENTRY_DEVICE_JWT_EXPIRY_IN_SECONDS: int = env.int(
        "SEND_ENTRY_DEVICE_JWT_EXPIRY_IN_SECONDS", 86400
    )  # 24hr
    MAX_ACTIVATION_ATTEMPTS: int = env.int("MAX_ACTIVATION_ATTEMPTS", 10)
    MOCK_GDM_PATIENT_SCOPE: Optional[str] = env.str("MOCK_GDM_PATIENT_SCOPE", None)
    MOCK_SEND_ENTRY_CLINICIAN_SCOPE: Optional[str] = env.str(
        "MOCK_SEND_ENTRY_CLINICIAN_SCOPE", None
    )
    MOCK_SEND_ENTRY_DEVICE_SCOPE: Optional[str] = env.str(
        "MOCK_SEND_ENTRY_DEVICE_SCOPE", None
    )
    RSA_PRIVATE_KEY: Optional[str] = env.str("RSA_PRIVATE_KEY", None)
    HS_KEY: Optional[str] = env.str("HS_KEY", None)


def init_config(app: Flask) -> None:
    app.config.from_object(Configuration)
    if app.config["RSA_PRIVATE_KEY"] is None and app.config["HS_KEY"] is None:
        raise ValueError(
            "No encryption method specified, either set HS_KEY or both RSA_PUBLIC_KEY and RSA_PRIVATE_KEY"
        )

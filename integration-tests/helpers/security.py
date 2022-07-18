from datetime import datetime, timedelta

from environs import Env
from jose import jwt as jose_jwt


def generate_system_jwt() -> str:
    return jose_jwt.encode(
        claims={
            "metadata": {"system_id": "integration-tests"},
            "iss": "http://localhost/",
            "aud": "http://localhost/",
            "scope": Env().str("SYSTEM_JWT_SCOPE"),
            "exp": datetime.utcnow() + timedelta(seconds=300),
        },
        key=Env().str("HS_KEY"),
        algorithm="HS512",
    )

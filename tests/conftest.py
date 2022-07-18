import copy
import uuid
from typing import Any, Dict, Generator, Optional, Tuple, Type

import pytest
from flask import Flask, g
from flask.ctx import AppContext
from mock import Mock
from pytest_mock import MockerFixture, MockFixture


@pytest.fixture
def app() -> Flask:
    """ "Fixture that creates app for testing"""
    from dhos_activation_auth_api.app import create_app

    return create_app(testing=True, use_pgsql=False, use_sqlite=True)


@pytest.fixture
def app_context(app: Flask) -> Generator[None, None, None]:
    with app.app_context():
        g.jwt_claims = {}
        g.jwt_scopes = []
        yield


@pytest.fixture(autouse=True)
def mock_bearer_validation(mocker: MockFixture) -> Mock:
    return mocker.patch(
        "jose.jwt.get_unverified_claims",
        return_value={
            "sub": "1234567890",
            "name": "John Doe",
            "iat": 1_516_239_022,
            "iss": "http://localhost/",
        },
    )


@pytest.fixture
def redis_values() -> Dict:
    return {}


@pytest.fixture
def mock_dhosredis(monkeypatch: Any, redis_values: Dict) -> Type:
    import dhosredis

    copy.deepcopy(redis_values)

    class MockRedis:
        @classmethod
        def get_value(cls, key: str) -> Optional[str]:
            return redis_values.get(key)

        @classmethod
        def set_value(cls, key: str, value: str) -> None:
            redis_values[key] = value

    monkeypatch.setattr(dhosredis, "DhosRedis", MockRedis)
    return MockRedis


@pytest.fixture
def sample_clinician() -> Dict:
    return {
        "clinician_id": "123ABC",
        "send_entry_identifier": "12345ABC",
        "login_active": True,
        "groups": ["send superclinician"],
        "products": ["SEND"],
    }


@pytest.fixture
def sample_clinician_update() -> Dict:
    return {
        "send_entry_identifier": "12345ABC",
        "login_active": True,
        "contract_expiry_eod_date": "2050-01-01",
        "groups": ["send superclinician"],
        "products": ["SEND"],
    }


@pytest.fixture
def mock_retrieve_jwt_claims(app: Flask, mocker: MockerFixture) -> Mock:
    from flask_batteries_included.helpers.security import _ProtectedRoute

    def mock_claims(self: Any, verify: bool = True) -> Tuple:
        return g.jwt_claims, g.jwt_scopes

    app.config["IGNORE_JWT_VALIDATION"] = False

    return mocker.patch.object(_ProtectedRoute, "_retrieve_jwt_claims", mock_claims)


@pytest.fixture
def device_jwt_uuid(app_context: AppContext, mocker: MockFixture) -> str:
    """Use this fixture to make requests with a device JWT"""
    device_uuid = str(uuid.uuid4())
    mocker.patch.object(g, "jwt_claims", {"device_id": device_uuid, "sub": device_uuid})
    # flask.g.jwt_claims = {"device_id": device_uuid, "sub": device_uuid}
    mocker.patch.object(
        g,
        "jwt_scopes",
        "read:send_device read:send_entry_identifier read:send_location",
    )
    # flask.g.jwt_scopes = "read:send_device read:send_entry_identifier read:send_location"
    return device_uuid

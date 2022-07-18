from typing import Any

import pytest
from flask import current_app as app
from flask_batteries_included.helpers.error_handler import ServiceUnavailableException
from mock import Mock

from dhos_activation_auth_api.blueprint_api.scopes import (
    get_gdm_patient_scope,
    get_send_entry_clinician_scope,
)


@pytest.mark.usefixtures("app_context")
class TestScopes:
    def test_get_gdm_patient_scope_cached(self, mock_dhosredis: Mock) -> None:
        mock_dhosredis.set_value("CACHED_GDM_PATIENT_SCOPE", "cached")
        scope = get_gdm_patient_scope()
        assert scope == "cached"

    def test_get_gdm_patient_scope(self, mock_dhosredis: Mock) -> None:
        mock_dhosredis.set_value("CACHED_GDM_PATIENT_SCOPE", None)
        expected = "write:mock1 read:mock2"
        actual: str = get_gdm_patient_scope()
        assert actual == expected

    def test_get_send_entry_scope_cached(self, mock_dhosredis: Mock) -> None:
        mock_dhosredis.set_value("CACHED_SEND_ENTRY_CLINICIAN_SCOPE", "cached")
        scope = get_send_entry_clinician_scope()
        assert scope == "cached"

    def test_get_send_entry_scope(self, mock_dhosredis: Mock) -> None:
        mock_dhosredis.set_value("CACHED_SEND_ENTRY_CLINICIAN_SCOPE", None)
        expected = "write:mock3 read:mock4"
        actual: str = get_send_entry_clinician_scope()
        assert actual == expected

    def test_auth0_failure_dev_get_mock_scope(self, mock_dhosredis: Mock) -> None:
        mock_dhosredis.set_value("CACHED_GDM_PATIENT_SCOPE", None)
        expected = app.config["MOCK_GDM_PATIENT_SCOPE"]
        actual: str = get_gdm_patient_scope()
        assert actual == expected

    def test_auth0_failure_prod_get_mock_scope(
        self, monkeypatch: Any, mock_dhosredis: Mock
    ) -> None:
        mock_dhosredis.set_value("CACHED_GDM_PATIENT_SCOPE", None)
        monkeypatch.setenv("ENVIRONMENT", "something production like")
        with pytest.raises(ServiceUnavailableException):
            get_gdm_patient_scope()

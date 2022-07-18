import datetime

import pytest
from flask_batteries_included.sqldb import db

from dhos_activation_auth_api.models.clinician import Clinician


@pytest.mark.usefixtures("app")
def test_contract_expiry_eod_date() -> None:
    uuid = "some-uuid"
    clinician_id = "123-456-789"

    obj = Clinician()
    obj.uuid = uuid
    obj.clinician_id = clinician_id
    obj.login_active = True
    obj.contract_expiry_eod_date = "1991-10-02"
    db.session.add(obj)
    db.session.commit()

    clinician = Clinician.query.filter_by(clinician_id=clinician_id).first()
    assert clinician.contract_expiry_eod_date_ == datetime.date(
        year=1991, month=10, day=2
    )
    assert clinician.contract_expiry_eod_date == "1991-10-02"

from typing import Dict, Optional

from flask_batteries_included.helpers.timestamp import (
    parse_date_to_iso8601,
    parse_iso8601_to_date,
)
from flask_batteries_included.sqldb import ModelIdentifier, db

clinician_group_table = db.Table(
    "clinician_group",
    db.Column("group_id", db.String, db.ForeignKey("group.uuid"), nullable=False),
    db.Column(
        "clinician_id", db.String, db.ForeignKey("clinician.uuid"), nullable=False
    ),
)

clinician_product_table = db.Table(
    "clinician_product",
    db.Column("product_id", db.String, db.ForeignKey("product.uuid"), nullable=False),
    db.Column(
        "clinician_id", db.String, db.ForeignKey("clinician.uuid"), nullable=False
    ),
)


class Clinician(ModelIdentifier, db.Model):

    __tablename__ = "clinician"

    clinician_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    login_active = db.Column(db.Boolean, nullable=False)
    send_entry_identifier = db.Column(db.String(50), nullable=True)

    contract_expiry_eod_date_ = db.Column(
        "contract_expiry_eod_date", db.Date(), nullable=True
    )

    products = db.relationship(
        "Product", secondary=clinician_product_table, backref="clinicians"
    )
    groups = db.relationship(
        "Group", secondary=clinician_group_table, backref="clinicians"
    )

    @classmethod
    def schema(cls) -> Dict:
        return {
            "optional": {
                "groups": [str],
                "contract_expiry_eod_date": str,
                "send_entry_identifier": str,
            },
            "required": {
                "clinician_id": str,
                "login_active": bool,
                "products": [str],
            },
            "updatable": {
                "login_active": bool,
                "send_entry_identifier": str,
                "products": list,
                "groups": list,
                "contract_expiry_eod_date": str,
            },
        }

    @property
    def contract_expiry_eod_date(self) -> Optional[str]:
        return parse_date_to_iso8601(self.contract_expiry_eod_date_)

    @contract_expiry_eod_date.setter
    def contract_expiry_eod_date(self, v: str) -> None:
        self.contract_expiry_eod_date_ = parse_iso8601_to_date(v)

from datetime import datetime
from typing import Dict, Optional

from flask_batteries_included.helpers.timestamp import join_timestamp
from flask_batteries_included.sqldb import ModelIdentifier, db


class PatientActivation(ModelIdentifier, db.Model):

    patient_id = db.Column(
        db.String(36), db.ForeignKey("patient.patient_id"), index=True
    )
    patient = db.relationship(
        "Patient", backref="activation", lazy=False, uselist=False
    )

    code = db.Column(db.String(36), nullable=False, index=True)
    hashed_otp = db.Column(db.LargeBinary(256), nullable=False)
    otp_salt = db.Column(db.String, nullable=True)

    used = db.Column(db.Boolean, nullable=False, default=False)
    attempts_count = db.Column(db.SmallInteger, nullable=False, default=0)

    activated_timestamp = db.Column(db.DateTime, unique=False, nullable=True)
    activated_timezone = db.Column(db.Integer, unique=False, nullable=True)

    def get_activated_timestamp(self) -> Optional[datetime]:
        if self.activated_timestamp is None:
            return None
        return join_timestamp(self.activated_timestamp, self.activated_timezone)

    @property
    def modified_by(self) -> str:
        return self.modified_by_

    @modified_by.setter
    def modified_by(self, v: str) -> None:
        self.modified_by_ = v

    @staticmethod
    def schema() -> Dict:
        return {
            "optional": {
                "patient_id": str,
                "patient": str,
                "code": str,
                "hashed_otp": str,
                "otp_salt": str,
                "used": str,
                "attempts_count": str,
            },
            "required": {},
            "updatable": {
                "patient_id": str,
                "patient": str,
                "code": str,
                "hashed_otp": str,
                "otp_salt": str,
                "used": str,
                "attempts_count": str,
            },
        }

    def to_dict(self) -> Dict:
        return {
            "activation_completed": self.get_activated_timestamp(),
            **self.pack_identifier(),
        }

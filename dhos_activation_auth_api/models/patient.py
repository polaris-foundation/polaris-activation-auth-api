from typing import Dict

from flask_batteries_included.sqldb import ModelIdentifier, db


class Patient(ModelIdentifier, db.Model):

    patient_id = db.Column(db.String(36), unique=True, nullable=False)
    email_address = db.Column(db.String, unique=True, nullable=True)
    phone_number = db.Column(db.String, unique=True, nullable=True)

    hashed_authorisation_code = db.Column(db.LargeBinary(256), nullable=True)
    authorisation_code_salt = db.Column(db.String, nullable=True)

    def to_dict(self) -> Dict:
        return {**self.pack_identifier()}

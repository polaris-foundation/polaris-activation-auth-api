from typing import Dict

from flask_batteries_included.sqldb import ModelIdentifier, db


class Device(ModelIdentifier, db.Model):
    location_id = db.Column(db.String(), nullable=False, unique=False)
    description = db.Column(db.String(), nullable=False, unique=False)
    hashed_authorisation_code = db.Column(
        db.LargeBinary(256), nullable=True, unique=True
    )
    authorisation_code_salt = db.Column(db.String(), nullable=True, unique=True)
    active = db.Column(db.Boolean(), nullable=False, unique=False, default=True)

    @classmethod
    def schema(cls) -> Dict:
        return {
            "optional": {},
            "required": {"description": str, "location_id": str},
            "updatable": {"description": str, "location_id": str, "active": bool},
        }

    def to_dict(self) -> Dict:
        return {
            **self.pack_identifier(),
            "location_id": self.location_id,
            "description": self.description,
            "active": self.active,
        }

    def __repr__(self) -> str:
        return f"Device(uuid={self.uuid}, location_id={self.location_id}, description={self.description})"

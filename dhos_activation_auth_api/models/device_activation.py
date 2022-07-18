from datetime import datetime
from typing import Dict, Optional

from flask_batteries_included.helpers.timestamp import join_timestamp
from flask_batteries_included.sqldb import ModelIdentifier, db


class DeviceActivation(ModelIdentifier, db.Model):

    device_id = db.Column(db.String(36), db.ForeignKey("device.uuid"))
    device = db.relationship("Device", backref="activation", lazy=False, uselist=False)

    code = db.Column(db.String(36), nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)

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
        return {"optional": {}, "required": {}, "updatable": {}}

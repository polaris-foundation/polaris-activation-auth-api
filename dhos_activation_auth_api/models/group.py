from flask_batteries_included.sqldb import ModelIdentifier, db


class Group(ModelIdentifier, db.Model):
    __tablename__ = "group"

    name = db.Column(db.String(20), unique=True, nullable=False)

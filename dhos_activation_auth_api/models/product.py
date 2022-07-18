from flask_batteries_included.sqldb import ModelIdentifier, db


class Product(ModelIdentifier, db.Model):
    __tablename__ = "product"

    name = db.Column(db.String(20), unique=True, nullable=False)

from flask_batteries_included.sqldb import db


def reset_database() -> None:
    session = db.session
    session.execute("TRUNCATE TABLE clinician cascade")
    session.execute("TRUNCATE TABLE patient_activation cascade")
    session.execute("TRUNCATE TABLE patient cascade")
    session.execute("TRUNCATE TABLE device_activation cascade")
    session.execute("TRUNCATE TABLE device cascade")
    session.commit()
    session.close()

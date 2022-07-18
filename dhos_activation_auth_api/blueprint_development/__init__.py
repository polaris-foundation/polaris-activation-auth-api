import time

from flask import Blueprint, Response, current_app, g, jsonify
from flask_batteries_included.helpers.security import protected_route
from flask_batteries_included.helpers.security.endpoint_security import (
    key_present,
    match_keys,
)

from .controller import reset_database

development_blueprint = Blueprint("dev", __name__)


@development_blueprint.route("/drop_data", methods=["POST"])
@protected_route(key_present("system_id"))
def drop_data_route() -> Response:
    if current_app.config["ALLOW_DROP_DATA"] is not True:
        raise PermissionError("Cannot drop data in this environment")

    start: float = time.time()
    reset_database()
    total_time: float = time.time() - start
    return jsonify({"complete": True, "time_taken": str(total_time) + "s"})


@development_blueprint.route("/dhos/v1/patient/<patient_id>/security-info")
@protected_route(verify=False)
def security_info(patient_id: str) -> Response:
    return jsonify({"patient_id_in_url": patient_id, "jwt": g.jwt_claims})


@development_blueprint.route("/dhos/v1/patient/<patient_id>/security-test")
@protected_route(match_keys(patient_id="patient_id"))
def security_test(patient_id: str) -> str:
    return "You passed in a valid JWT for patient_id " + patient_id

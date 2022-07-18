import uuid
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from flask import current_app as app
from flask_batteries_included.config import (
    is_not_production_environment,
    is_production_environment,
)
from flask_batteries_included.helpers.error_handler import (
    DuplicateResourceException,
    EntityNotFoundException,
)
from flask_batteries_included.helpers.security.jwt import current_jwt_user
from flask_batteries_included.sqldb import db, generate_uuid
from jose import jwt as jose_jwt
from she_logging import logger

from dhos_activation_auth_api.blueprint_api import audit
from dhos_activation_auth_api.blueprint_api.scopes import (
    get_gdm_patient_scope,
    get_send_entry_clinician_scope,
    get_send_entry_device_scope,
)
from dhos_activation_auth_api.helpers.utils import (
    calculate_end_of_day_expiry,
    check_device_activation_valid,
    check_patient_activation_valid,
    generate_seconds_from_now_expiry,
    generate_secure_human_readable_string,
    generate_secure_numeric_string,
    generate_secure_random_string,
    hash_ascii_with_salt,
    is_static_device_id,
    is_static_patient_id,
)
from dhos_activation_auth_api.models.clinician import Clinician
from dhos_activation_auth_api.models.device import Device
from dhos_activation_auth_api.models.device_activation import DeviceActivation
from dhos_activation_auth_api.models.group import Group
from dhos_activation_auth_api.models.patient import Patient
from dhos_activation_auth_api.models.patient_activation import PatientActivation
from dhos_activation_auth_api.models.product import Product


def create_patient_activation(patient_id: str) -> Dict:
    existing_activation: Optional[
        PatientActivation
    ] = PatientActivation.query.filter_by(patient_id=patient_id, used=False).first()

    if is_not_production_environment() and is_static_patient_id(patient_id):
        return _reset_static_activation(patient_id, existing_activation)

    # Existing activations have their data regenerated.
    if existing_activation:

        # Reset attempts count
        existing_activation.attempts_count = 0

        # Bump the activation updated date, to extend its life
        existing_activation.modified = datetime.utcnow()

        otp = generate_secure_human_readable_string(app.config["OTP_LENGTH"]).lower()
        otp_salt = generate_secure_random_string(app.config["SALT_LENGTH"])
        hashed_otp = hash_ascii_with_salt(otp, otp_salt)

        # Add new OTP
        existing_activation.otp_salt = otp_salt
        existing_activation.hashed_otp = hashed_otp

        db.session.add(existing_activation)
        db.session.commit()

        return {
            "otp": otp,
            "activation_code": existing_activation.code,
            "expires_at": calculate_end_of_day_expiry(
                datetime.utcnow(), app.config["ACTIVATION_EXPIRY_END_OF_NTH_DAY"]
            ),
        }

    # New activations are created
    else:

        # Check if the patient is already in the database
        existing_user: Optional[Patient] = Patient.query.filter_by(
            patient_id=patient_id
        ).first()

        # Create activation code
        internal_code = generate_secure_random_string(
            app.config["AUTHORISATION_CODE_LENGTH"]
        )
        # Create lowercase OTP
        otp = generate_secure_human_readable_string(app.config["OTP_LENGTH"]).lower()
        otp_salt = generate_secure_random_string(app.config["SALT_LENGTH"])
        hashed_otp = hash_ascii_with_salt(otp, otp_salt)

        # Save to database

        # Create patient if necessary
        if not existing_user:
            patient = Patient(uuid=generate_uuid(), patient_id=patient_id)
            db.session.add(patient)

        # Create activation
        activation = PatientActivation(
            uuid=generate_uuid(),
            patient_id=patient_id,
            code=internal_code,
            otp_salt=otp_salt,
            hashed_otp=hashed_otp,
        )

        db.session.add(activation)
        db.session.commit()

        # Return OTP and activation code
        return {
            "otp": otp,
            "activation_code": internal_code,
            "expires_at": calculate_end_of_day_expiry(
                datetime.utcnow(), app.config["ACTIVATION_EXPIRY_END_OF_NTH_DAY"]
            ),
        }


def get_patient_activations(patient_id: str) -> List[Dict]:
    completed_activations = (
        PatientActivation.query.filter(
            PatientActivation.patient_id == patient_id, PatientActivation.used == True
        )
        .order_by(PatientActivation.activated_timestamp.desc())
        .all()
    )

    return [item.to_dict() for item in completed_activations]


def update_patient_activation(code: str, otp: str) -> Dict:

    # Get activation if not used and previous attempts count <= 10
    existing_activation: Optional[PatientActivation] = PatientActivation.query.filter(
        PatientActivation.code == code,
        PatientActivation.used == False,
        PatientActivation.attempts_count < app.config["MAX_ACTIVATION_ATTEMPTS"],
    ).first()

    # Check OTP - if no match, increment attempts count in the database and trigger entity not found exception
    if (
        existing_activation is not None
        and existing_activation.hashed_otp
        != hash_ascii_with_salt(otp, existing_activation.otp_salt)
    ):
        logger.debug("Incorrect hash supplied")

        existing_activation.attempts_count += 1
        db.session.add(existing_activation)
        db.session.commit()

        existing_activation = None

    if not check_patient_activation_valid(
        existing_activation, app.config["ACTIVATION_EXPIRY_END_OF_NTH_DAY"]
    ):
        raise EntityNotFoundException("Could not find relevant activation")

    if existing_activation is None:
        # This is to satisfy type checking.
        raise EntityNotFoundException("Could not find relevant activation")

    authorisation_code = generate_secure_random_string(
        app.config["AUTHORISATION_CODE_LENGTH"]
    )
    authorisation_code_salt = generate_secure_random_string(app.config["SALT_LENGTH"])
    hashed_authorisation_code = hash_ascii_with_salt(
        authorisation_code, authorisation_code_salt
    )

    existing_activation.patient.hashed_authorisation_code = hashed_authorisation_code
    existing_activation.patient.authorisation_code_salt = authorisation_code_salt

    # Mark activation as used unless in non-prod and patient ID is static
    if is_production_environment() or not is_static_patient_id(
        existing_activation.patient_id
    ):
        existing_activation.used = True

    existing_activation.modified_by = existing_activation.patient.patient_id
    # default activated date to current server time
    existing_activation.activated_timestamp = datetime.utcnow()
    existing_activation.activated_timezone = 0
    db.session.add(existing_activation)
    db.session.commit()

    return {
        "authorisation_code": authorisation_code,
        "patient_id": existing_activation.patient.patient_id,
    }


def get_patient_jwt(patient_id: str, code: str) -> Dict:
    patient: Optional[Patient] = Patient.query.filter_by(patient_id=patient_id).first()

    if not patient:
        logger.info("Patient not found with UUID %s", patient_id)
        raise EntityNotFoundException("Invalid combination of patient_id and code")

    hashed_authorisation_code = hash_ascii_with_salt(
        code, patient.authorisation_code_salt
    )

    if patient.hashed_authorisation_code != hashed_authorisation_code:
        logger.info("Patient provided incorrect authorisation code")
        logger.debug(
            "Could not match authorisation hash",
            extra={
                "provided_hash": hashed_authorisation_code,
                "expected_hash": patient.hashed_authorisation_code,
            },
        )
        raise EntityNotFoundException("Invalid combination of patient_id and code")

    key, alg, iss = _retrieve_key_alg_iss_for_signing()

    jwt_payload = {
        "metadata": {"patient_id": patient_id},
        "iss": iss,
        "aud": iss,
        "scope": get_gdm_patient_scope(),
        "exp": generate_seconds_from_now_expiry(app.config["JWT_EXPIRY_IN_SECONDS"]),
    }
    return {"jwt": jose_jwt.encode(claims=jwt_payload, key=key, algorithm=alg)}


def create_clinician(clinician: Dict) -> None:

    # Check a clinician with this clinician ID doesn't already exist
    clinician_db = Clinician.query.filter_by(
        clinician_id=clinician["clinician_id"]
    ).first()
    if clinician_db is not None:
        raise DuplicateResourceException(
            "Clinician with that clinician_id already present"
        )

    # Create a list of Product and Group entities for the clinician
    products: List[Product] = _get_or_create_products(
        [p.lower() for p in clinician.pop("products")]
    )
    groups: List[Group] = _get_or_create_groups(
        [g.lower() for g in clinician.pop("groups")]
    )

    c: Clinician = Clinician(**clinician)
    c.uuid = generate_uuid()
    c.products = products
    c.groups = groups

    db.session.add(c)
    db.session.commit()


def update_clinician(clinician_id: str, clinician: Dict) -> None:

    # We select by clinician_id here (rather than UUID) because clinician_id correlates
    # with clinician.uuid in dhos-services-api. The UUID here is specific to this database.
    clinician_db = Clinician.query.filter_by(clinician_id=clinician_id).first_or_404()

    # Create a list of Product and Group entities for the clinician
    products: List[Product] = _get_or_create_products(
        [p.lower() for p in clinician.pop("products")]
    )
    groups: List[Group] = _get_or_create_groups(
        [g.lower() for g in clinician.pop("groups")]
    )

    if "login_active" in clinician:
        clinician_db.login_active = clinician["login_active"]
    clinician_db.contract_expiry_eod_date = clinician.get(
        "contract_expiry_eod_date", None
    )
    clinician_db.send_entry_identifier = clinician.get("send_entry_identifier")
    clinician_db.products = products
    clinician_db.groups = groups

    db.session.add(clinician_db)
    db.session.commit()


def _get_or_create_products(product_names: List[str]) -> List[Product]:
    products = []
    for product_name in product_names:
        product: Optional[Product] = Product.query.filter(
            Product.name == product_name
        ).first()
        if product is None:
            product = Product(uuid=generate_uuid(), name=product_name)
            db.session.add(product)
        products.append(product)
    return products


def _get_or_create_groups(group_names: List[str]) -> List[Group]:
    groups = []
    for group_name in group_names:
        group: Optional[Group] = Group.query.filter(Group.name == group_name).first()
        if group is None:
            group = Group(uuid=generate_uuid(), name=group_name)
            db.session.add(group)
        groups.append(group)
    return groups


def clinician_has_send_entry_access(clinician: Clinician) -> bool:
    for group in clinician.groups:
        if group.name.lower() in ("send clinician", "send superclinician"):
            return True
    return False


def create_clinician_jwt(
    send_entry_identifier: str, device_uuid: str
) -> Dict[str, str]:
    clinician: Optional[Clinician] = Clinician.query.filter_by(
        send_entry_identifier=send_entry_identifier
    ).first()

    if clinician is None:
        logger.info(
            "Clinician not found with SEND Entry identifier '%s'", send_entry_identifier
        )
        # Create failed audit message
        audit.record_sendentry_login_failure(
            device_id=device_uuid,
            reason="Clinician with provided SEND Entry identifier not found",
            send_entry_identifier=send_entry_identifier,
        )
        raise EntityNotFoundException("Invalid clinician identifier")

    if (
        clinician.contract_expiry_eod_date_ is not None
        and date.today() > clinician.contract_expiry_eod_date_
        and clinician.login_active
    ):
        # Clinician is a temporary user whose access has expired. Mark the login as inactive.
        clinician.login_active = False
        db.session.commit()

    if clinician.login_active is False:
        audit.record_sendentry_login_failure(
            device_id=device_uuid,
            reason="Clinician contract expired",
            send_entry_identifier=send_entry_identifier,
            clinician_id=clinician.clinician_id,
        )
        raise PermissionError("Clinician is not active")

    if not clinician_has_send_entry_access(clinician):
        logger.info(
            "Unauthorized clinician attempted to access SEND Entry using identifier '%s'",
            send_entry_identifier,
        )
        raise PermissionError("Clinician is not authorised to access SEND Entry")

    # Create audit message.
    audit.record_sendentry_login_success(
        device_id=device_uuid,
        clinician_id=clinician.clinician_id,
        send_entry_identifier=send_entry_identifier,
    )

    key, alg, iss = _retrieve_key_alg_iss_for_signing()

    jwt_payload = {
        "metadata": {
            "clinician_id": clinician.clinician_id,
            "referring_device_id": device_uuid,
        },
        "iss": iss,
        "aud": iss,
        "scope": get_send_entry_clinician_scope(),
        "exp": generate_seconds_from_now_expiry(app.config["JWT_EXPIRY_IN_SECONDS"]),
    }
    return {"jwt": jose_jwt.encode(claims=jwt_payload, key=key, algorithm=alg)}


def _retrieve_key_alg_iss_for_signing() -> Tuple[str, str, str]:
    issuer = app.config["HS_ISSUER"]

    rsa_private_key = app.config.get("RSA_PRIVATE_KEY", None)
    if rsa_private_key is None:
        hs_key = app.config["HS_KEY"]
        return hs_key, "HS512", issuer
    else:
        return rsa_private_key, "RS256", issuer


def _reset_static_activation(
    patient_id: str, activation: PatientActivation = None
) -> Dict:
    """
    Creates or resets a static activation for a static patient. This is required because
    static patients have a special activation code that never changes and is reusable.
    """
    logger.debug("Resetting static activation for patient with UUID %s", patient_id)
    static_id: str = patient_id[-1]
    otp = (static_id * app.config["OTP_LENGTH"])[: app.config["OTP_LENGTH"]]

    if activation is None:
        logger.debug("Creating new activation for patient with UUID %s", patient_id)
        otp_salt = generate_secure_random_string(app.config["SALT_LENGTH"])
        hashed_otp = hash_ascii_with_salt(otp, otp_salt)

        # Create the activation.
        activation = PatientActivation(
            uuid=generate_uuid(),
            code=static_id,
            otp_salt=otp_salt,
            hashed_otp=hashed_otp,
            patient_id=patient_id,
            activated_timezone=0,
            activated_timestamp=datetime.utcnow(),
            created_by_="dhos-activation-auth-api",
            modified_by_="dhos-activation-auth-api",
        )

        logger.debug(
            "Created activation for patient with UUID %s",
            patient_id,
            extra={
                "activation_uuid": activation.uuid,
                "activation_code": activation.code,
            },
        )

        # Check if the patient is already in the database
        existing_user: Optional[Patient] = Patient.query.filter_by(
            patient_id=patient_id
        ).first()
        if existing_user is None:
            # Add the patient to the database.
            logger.debug("Creating database entry for patient with UUID %s", patient_id)
            authorisation_code_salt = static_id * app.config["SALT_LENGTH"]
            hashed_authorisation_code = hash_ascii_with_salt(
                static_id, authorisation_code_salt
            )
            patient = Patient(
                uuid=generate_uuid(),
                patient_id=patient_id,
                hashed_authorisation_code=hashed_authorisation_code,
                authorisation_code_salt=authorisation_code_salt,
                created_by_="dhos-activation-auth-api",
                modified_by_="dhos-activation-auth-api",
            )
            db.session.add(patient)

    db.session.add(activation)
    db.session.commit()

    return {
        "otp": otp,
        "activation_code": activation.code,
        "expires_at": calculate_end_of_day_expiry(
            datetime.utcnow(), app.config["ACTIVATION_EXPIRY_END_OF_NTH_DAY"]
        ),
    }


def create_device(device_details: Dict, device_type: Optional[str]) -> Dict:
    # TODO as more products are added, device_type will be used (remove leading underscore)
    if "uuid" not in device_details:
        device_details["uuid"] = str(uuid.uuid4())
    device = Device(**device_details)
    db.session.add(device)
    db.session.commit()
    return device.to_dict()


def get_device(device_id: str) -> Dict:
    device = Device.query.filter_by(uuid=device_id).first_or_404()
    return device.to_dict()


def update_device(device_id: str, _json: Dict) -> Dict:
    device = Device.query.filter_by(uuid=device_id).first_or_404()
    for key in _json:
        setattr(device, key, _json[key])
    db.session.add(device)
    db.session.commit()

    audit.record_sendentry_device_update(
        device_id=device.uuid,
        clinician_id=current_jwt_user(),
        updated_fields=_json,
    )
    return device.to_dict()


def get_devices(
    _device_type: Optional[str], active: bool, location_id: Optional[str]
) -> List[Dict]:
    # TODO as more products are added, device_type will be used (remove leading underscore)

    devices = Device.query.filter(Device.active.is_(active))

    if location_id is not None:
        location_ids = location_id.split(",")
        devices = devices.filter(Device.location_id.in_(location_ids))

    return [d.to_dict() for d in devices.all()]


def create_device_activation(device_id: str) -> Dict:
    Device.query.filter_by(uuid=device_id).first_or_404()

    existing_activation = DeviceActivation.query.filter_by(
        device_id=device_id, used=False
    ).first()

    if not is_production_environment() and is_static_device_id(device_id):
        # Static activation, so return the static code for this device.
        code = device_id[-1] * 9
    else:
        # Generate a new activation code.
        code = generate_secure_numeric_string(
            app.config["SEND_ENTRY_ACTIVATION_CODE_LENGTH"]
        ).lower()

    # TODO use global salt and hash activation code

    if existing_activation:
        existing_activation.modified = datetime.utcnow()
        existing_activation.code = code
        db.session.add(existing_activation)
    else:
        activation = DeviceActivation(
            uuid=generate_uuid(), device_id=device_id, code=code, used=False
        )
        db.session.add(activation)
    db.session.commit()

    return {
        "code": code,
        "expires_at": calculate_end_of_day_expiry(
            datetime.utcnow(), app.config["ACTIVATION_EXPIRY_END_OF_NTH_DAY"]
        ),
    }


def update_device_activation(activation_code: str, _device_type: Optional[str]) -> Dict:
    # TODO as more products are added, device_type will be used (remove leading underscore)
    activation: Optional[DeviceActivation] = DeviceActivation.query.filter_by(
        code=activation_code, used=False
    ).first()
    if activation is None:
        logger.info("Invalid activation code supplied")

    if not check_device_activation_valid(
        activation, app.config["ACTIVATION_EXPIRY_END_OF_NTH_DAY"]
    ):
        raise EntityNotFoundException("Could not find relevant activation")

    if activation is None:
        # This is to satisfy type checking.
        raise EntityNotFoundException("Could not find relevant activation")

    authorisation_code = generate_secure_random_string(
        app.config["AUTHORISATION_CODE_LENGTH"]
    )

    authorisation_code_salt = generate_secure_random_string(app.config["SALT_LENGTH"])
    hashed_auth_code = hash_ascii_with_salt(authorisation_code, authorisation_code_salt)

    activation.device.hashed_authorisation_code = hashed_auth_code
    activation.device.authorisation_code_salt = authorisation_code_salt

    # Mark activation as used unless it's a static device in a non-production environment.
    if is_production_environment() or not is_static_device_id(activation.device.uuid):
        activation.used = True

    db.session.add(activation)
    db.session.commit()

    return {
        "authorisation_code": authorisation_code,
        "device_id": activation.device.uuid,
    }


def get_device_jwt(device_id: str, authorisation_code: str) -> Dict:
    device: Optional[Device] = Device.query.filter_by(uuid=device_id).first()
    if not device:
        raise PermissionError("Invalid device ID")

    if (
        device.hashed_authorisation_code is None
        or device.authorisation_code_salt is None
    ):
        logger.info(
            "Cannot get device JWT, device has not been activated: %s", device_id
        )
        # Create failed audit message
        audit.record_sendentry_device_auth_failure(
            device_id=device_id, reason="Device has not been activated"
        )
        raise PermissionError("Invalid device identifier")

    this_hash = hash_ascii_with_salt(authorisation_code, device.authorisation_code_salt)
    valid = this_hash == device.hashed_authorisation_code

    if not valid or not device.active:
        logger.info("Validation of auth code failed for device: %s", device_id)
        # Create failed audit message
        audit.record_sendentry_device_auth_failure(
            device_id=device_id, reason="Device auth code validation failed"
        )
        raise PermissionError("Could not retrieve JWT")

    audit.record_sendentry_device_auth_success(device_id=device.uuid)

    key, alg, iss = _retrieve_key_alg_iss_for_signing()

    jwt_payload = {
        "metadata": {"device_id": device.uuid},
        "iss": iss,
        "aud": iss,
        "scope": get_send_entry_device_scope(),
        "exp": generate_seconds_from_now_expiry(
            app.config["SEND_ENTRY_DEVICE_JWT_EXPIRY_IN_SECONDS"]
        ),
    }
    return {"jwt": jose_jwt.encode(claims=jwt_payload, key=key, algorithm=alg)}

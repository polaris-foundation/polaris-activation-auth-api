from typing import TypedDict

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask_batteries_included.helpers.apispec import (
    FlaskBatteriesPlugin,
    initialise_apispec,
    openapi_schema,
)
from marshmallow import EXCLUDE, Schema, fields

dhos_activation_auth_api_spec: APISpec = APISpec(
    version="1.0.0",
    openapi_version="3.0.3",
    title="DHOS Activation Auth API",
    info={
        "description": "The DHOS Activation Auth API is responsible for activation, authentication and authorisation of users via JWT."
    },
    plugins=[FlaskPlugin(), MarshmallowPlugin(), FlaskBatteriesPlugin()],
)

initialise_apispec(dhos_activation_auth_api_spec)


class Identifier(Schema):
    class Meta:
        class Dict(TypedDict, total=False):
            uuid: str
            created: str
            created_by: str
            modified: str
            modified_by: str

    uuid = fields.String(
        required=True,
        description="Universally unique identifier for object",
        example="2c4f1d24-2952-4d4e-b1d1-3637e33cc161",
    )
    created = fields.String(
        required=True,
        description="When the object was created",
        example="2017-09-23T08:29:19.123+00:00",
    )
    created_by = fields.String(
        required=True,
        description="UUID of the user that created the object",
        example="d26570d8-a2c9-4906-9c6a-ea1a98b8b80f",
    )
    modified = fields.String(
        required=True,
        description="When the object was modified",
        example="2017-09-23T08:29:19.123+00:00",
    )
    modified_by = fields.String(
        required=True,
        description="UUID of the user that modified the object",
        example="2a0e26e5-21b6-463a-92e8-06d7290067d0",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class ActivationResponse(Identifier):
    class Meta:
        title = "Activation response"
        unknown = EXCLUDE
        ordered = True

    otp = fields.String(
        required=True,
        description="The one time PIN for the activation",
        example="UG6L2",
    )
    activation_code = fields.String(
        required=True,
        description="The activation code to use when validating the activation",
        example="d84J7dGhJa5YI8435798w4dHf8skjd",
    )
    expires_at = fields.String(
        required=True,
        description="ISO8601 timestamp at which the activation expires",
        example="2018-03-26T23:59:59.000Z",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class ActivationHistory(Identifier):
    class Meta:
        title = "Activation history"
        unknown = EXCLUDE
        ordered = True

    activation_completed = fields.String(
        required=True,
        description="ISO8601 timestamp at which the activation was validated",
        example="2018-03-26T23:59:59.000Z",
    )


@openapi_schema(dhos_activation_auth_api_spec, {"nullable": True})
class AuthorisationRequest(Schema):
    class Meta:
        title = "Authorisation request"
        unknown = EXCLUDE
        ordered = True

    otp = fields.String(
        required=True,
        allow_none=True,
        description="The one time PIN for the activation",
        example="H3K5",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class ValidatePatientActivationResponse(Identifier):
    class Meta:
        title = "Authorisation response"
        unknown = EXCLUDE
        ordered = True

    authorisation_code = fields.String(
        required=True,
        description="Authorisation code used to request JWTs for this patient",
        example="YW3OFH7W398FH3WP98JF038WUGP927P2GSGA87985SG6D5F78FG",
    )
    patient_id = fields.String(
        required=True,
        description="UUID of patient this activation relates to",
        example="ab3d9aa3-d5aa-406a-87b2-cd67ad872724",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class ClinicianCreate(Schema):
    class Meta:
        title = "Clinician create"
        unknown = EXCLUDE
        ordered = True

    clinician_id = fields.String(
        required=True,
        description="The UUID of the clinician in DHOS Services",
        example="ab3d9aa3-d5aa-406a-87b2-cd67ad872724",
    )
    send_entry_identifier = fields.String(
        required=False,
        allow_none=True,
        description="Clinician's identifier for SEND Entry",
        example="666123",
    )
    login_active = fields.Boolean(
        required=True, description="Whether login is currently active", example=True
    )
    products = fields.List(
        fields.String(),
        required=True,
        description="Products the clinician is associated with",
        example=["GDM"],
    )
    groups = fields.List(
        fields.String(),
        required=False,
        description="Names of the groups the clinician belongs to",
        example=["GDM Superclinician"],
    )
    contract_expiry_eod_date = fields.String(
        required=False,
        allow_none=True,
        description="ISO8601 date of the clinician login expiry",
        example="2019-03-26",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class ClinicianPatch(Schema):
    class Meta:
        title = "Clinician update"
        unknown = EXCLUDE
        ordered = True

    send_entry_identifier = fields.String(
        required=False,
        allow_none=True,
        description="Clinician's identifier for SEND Entry",
        example="666123",
    )
    login_active = fields.Boolean(
        required=False, description="Whether login is currently active", example=True
    )
    products = fields.List(
        fields.String(),
        required=True,
        description="Products the clinician is associated with",
        example=["GDM"],
    )
    groups = fields.List(
        fields.String(),
        required=True,
        description="Names of the groups the clinician belongs to",
        example=["GDM Superclinician"],
    )
    contract_expiry_eod_date = fields.String(
        required=False,
        allow_none=True,
        description="ISO8601 date of the clinician login expiry",
        example="2019-03-26",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class JwtResponse(Identifier):
    class Meta:
        title = "JWT response"
        unknown = EXCLUDE
        ordered = True

    jwt = fields.String(
        required=True,
        description="JWT bearer token to authorise the user",
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class DeviceRequest(Schema):
    class Meta:
        title = "Device request"
        unknown = EXCLUDE
        ordered = True

    location_id = fields.String(
        required=True,
        description="the UUID of the location that holds the device",
        example="c4f1d24-2952-4d4e-b1d1-3637e33cc161",
    )

    description = fields.String(
        required=True,
        description="free text description of the device",
        example="Jon's SEND Tablet",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class DeviceResponse(Identifier, DeviceRequest):
    class Meta:
        title = "Device response"
        unknown = EXCLUDE
        ordered = True


@openapi_schema(dhos_activation_auth_api_spec)
class DeviceUpdate(Schema):
    class Meta:
        title = "Device update"
        unknown = EXCLUDE
        ordered = True

    location_id = fields.String(
        required=False,
        description="the UUID of the location that holds the device",
        example="c4f1d24-2952-4d4e-b1d1-3637e33cc161",
    )

    description = fields.String(
        required=False,
        description="free text description of the device",
        example="Jon's SEND Tablet",
    )

    active = fields.Boolean(
        required=False,
        description="Whether the device is currently active",
        example=False,
    )


@openapi_schema(dhos_activation_auth_api_spec)
class DeviceActivationResponse(Schema):
    class Meta:
        title = "Device activation response"
        unknown = EXCLUDE
        ordered = True

    code = fields.String(
        required=True,
        description="the activation code for the device",
        example="c4f1d2429524d4eb1d13637e33cc161",
    )

    description = fields.String(
        required=True,
        description="free text description of the device",
        example="Jon's SEND Tablet",
    )

    expires_at = fields.String(
        required=True,
        description="ISO8601 timestamp at which the activation expires",
        example="2018-03-26T23:59:59.000Z",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class ValidateDeviceActivationResponse(Schema):
    class Meta:
        title = "Validate device activation response"
        unknown = EXCLUDE
        ordered = True

    authorisation_code = fields.String(
        required=True,
        description="Device authorisation code",
        example="c4f1d2429524d4eb1d13637e33cc161",
    )

    device_id = fields.String(
        required=True,
        description="the UUID of the device that this auth code applies to",
        example="c4f1d24-2952-4d4e-b1d1-3637e33cc161",
    )


@openapi_schema(dhos_activation_auth_api_spec)
class Device(Identifier, DeviceRequest):
    class Meta:
        title = "Device response"
        unknown = EXCLUDE
        ordered = True

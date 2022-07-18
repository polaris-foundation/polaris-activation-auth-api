from typing import Dict, Optional

from flask import Blueprint, Response, g, jsonify, make_response, request
from flask_batteries_included.helpers import schema
from flask_batteries_included.helpers.request_arg import RequestArg
from flask_batteries_included.helpers.security import protected_route
from flask_batteries_included.helpers.security.endpoint_security import scopes_present

from dhos_activation_auth_api.blueprint_api import controller
from dhos_activation_auth_api.models.clinician import Clinician
from dhos_activation_auth_api.models.device import Device

api_blueprint = Blueprint("api", __name__)

# PATIENT


@api_blueprint.route("/dhos/v1/patient/<patient_id>/activation", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:gdm_activation"))
def create_patient_activation(patient_id: str) -> Response:
    """---
    post:
      summary: Create a new patient activation
      description: >-
        Create a new activation for a patient. Responds with a shortened URL
        and a one-time-pin, to be used once to validate the activation.
      tags: [patient-auth]
      parameters:
        - name: patient_id
          in: path
          required: true
          description: The UUID of the patient for which to create an activation
          schema:
            type: string
            example: ab3d9aa3-d5aa-406a-87b2-cd67ad872724
      responses:
        '200':
          description: Creates a patient activation
          content:
            application/json:
              schema: ActivationResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return jsonify(controller.create_patient_activation(patient_id))


@api_blueprint.route("/dhos/v1/patient/<patient_id>/activation", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:gdm_activation"))
def get_patient_activations(patient_id: str) -> Response:
    """---
    get:
      summary: Get a patient's activations
      description: >-
        Responds with a list of activations created for the specified patient
        UUID.
      tags: [patient-auth]
      parameters:
        - name: patient_id
          in: path
          required: true
          description: The UUID of the patient for which to retrive activations
          schema:
            type: string
            example: ab3d9aa3-d5aa-406a-87b2-cd67ad872724
      responses:
        '200':
          description: A list of patient activations
          content:
            application/json:
              schema:
                type: array
                items: ActivationHistory
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return jsonify(controller.get_patient_activations(patient_id))


# This endpoint is protected by an authorisation code, not a JWT
@api_blueprint.route("/dhos/v1/patient/<patient_id>/jwt", methods=["GET"])
def get_patient_jwt(patient_id: str) -> Response:
    """---
    get:
      summary: Get a JWT for a patient
      description: >-
        Responds with a valid patient JWT. Requires the `x-authorisation-code`
        header containing an authorisation code acquired by validating a patient
        activation.
      tags: [patient-auth]
      parameters:
        - name: patient_id
          in: path
          required: true
          description: UUID of the patient
          schema:
            type: string
            example: ab3d9aa3-d5aa-406a-87b2-cd67ad872724
        - name: x-authorisation-code
          in: header
          description: An authorisation header
          required: true
          schema:
            type: string
            example: 5kjhw45kjh74
      responses:
        '200':
          description: A structure containing a valid patient JWT
          content:
            application/json:
              schema: JwtResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    auth_code = request.headers.get("x-authorisation-code", None)
    if auth_code is None:
        raise ValueError("No x-authorisation-code header provided")
    return jsonify(controller.get_patient_jwt(patient_id, auth_code))


# CLINICIAN


@api_blueprint.route("/dhos/v1/clinician", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:send_clinician"))
def create_clinician() -> Response:
    """---
    post:
      summary: Create a clinician for device auth
      description: >-
        Create a clinician object, only to be used for storing clinician login
        details. Not to be confused with the clinician object in the Polaris Users API.
      tags: [clinician-auth]
      requestBody:
        description: Details of the clinician to save
        required: true
        content:
          application/json:
            schema: ClinicianCreate
      responses:
        '201':
          description: Clinician created successfully
        default:
          description: >-
              Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    clinician_details: Dict = schema.post(**Clinician.schema())
    controller.create_clinician(clinician_details)
    return make_response("", 201)


@api_blueprint.route("/dhos/v1/clinician/<clinician_id>", methods=["PATCH"])
@protected_route(scopes_present(required_scopes="write:send_clinician"))
def update_clinician(clinician_id: str) -> Response:
    """---
    patch:
      summary: Update a clinician instance for device auth
      description: >-
        Update a clinician object, only to be used for storing clinician login
        details.
      tags: [clinician-auth]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: UUID of the clinician to update
          schema:
            type: string
            example: ab3d9aa3-d5aa-406a-87b2-cd67ad872724
      requestBody:
        description: Details to update for the clinician
        required: true
        content:
          application/json:
            schema: ClinicianPatch
      responses:
        '200':
          description: Clinician updated successfully
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    clinician_details: Dict = schema.update(**Clinician.schema())
    controller.update_clinician(clinician_id, clinician_details)
    return make_response("", 200)


@api_blueprint.route("/dhos/v1/clinician/jwt", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:send_entry_identifier"))
def create_clinician_jwt(send_entry_identifier: str) -> Response:
    """---
    get:
      summary: Get a JWT for a clinician
      description: >-
        Responds with a valid clinician JWT. Requires a device JWT for
        authorisation.
      tags: [clinician-auth]
      parameters:
        - name: send_entry_identifier
          in: query
          required: true
          description: SEND entry identifier for the clinician
          schema:
            type: string
            example: ab3d9aa3-d5aa-406a-87b2-cd67ad872724
      responses:
        '200':
          description: A structure containing a valid clinician JWT
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JwtResponse'
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    # Get the device UUID from the device JWT used to authenticate this request.
    device_uuid: Optional[str] = g.jwt_claims.get("device_id", None)
    if device_uuid is None:
        raise PermissionError("Not a device")
    return jsonify(controller.create_clinician_jwt(send_entry_identifier, device_uuid))


# DEVICE


@api_blueprint.route("/dhos/v1/device", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:send_device"))
def create_device() -> Response:
    """---
    post:
      summary: Create a new device
      description: Create a known device containing details including location and name.
      tags: [device-auth]
      requestBody:
        description: The device information to save
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DeviceRequest'
      parameters:
        - name: type
          in: query
          required: false
          description: The device type
          schema:
            type: string
            example: send_entry
      responses:
        '200':
          description: Returns details of the created device
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DeviceResponse'
        default:
          description: >-
              Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    device_details = schema.post(**Device.schema())
    device_type: Optional[str] = request.args.get("type", None)
    return jsonify(controller.create_device(device_details, device_type))


@api_blueprint.route("/dhos/v1/device/<device_id>", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:send_device"))
def get_device_by_id(device_id: str) -> Response:
    """---
    get:
      summary: Get a device by UUID
      description: Get details of the known device with the specified UUID.
      tags: [device-auth]
      parameters:
        - name: device_id
          in: path
          required: true
          description: The device UUID
          schema:
            type: string
            example: cc71c130-dbc8-4961-a462-a491523a9f8c
      responses:
        '200':
          description: Details of the device
          content:
            application/json:
              schema: Device
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    if request.is_json:
        raise ValueError("Request should not contain a JSON body")
    return jsonify(controller.get_device(device_id))


@api_blueprint.route("/dhos/v1/device/<device_id>", methods=["PATCH"])
@protected_route(scopes_present(required_scopes="write:send_device"))
def update_device(device_id: str) -> Response:
    """---
    patch:
      summary: Update a device by UUID
      description: Update details of the known device with the specified UUID.
      tags: [device-auth]
      parameters:
        - name: device_id
          in: path
          required: true
          description: The id of the device to return
          schema:
            type: string
            example: cc71c130-dbc8-4961-a462-a491523a9f8c
      requestBody:
        description: device fields to update
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DeviceUpdate'
      responses:
        '200':
          description: An object containing the device details
          content:
            application/json:
              schema: Device
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    device_details = schema.update(**Device.schema())
    return jsonify(controller.update_device(device_id, device_details))


@api_blueprint.route("/dhos/v1/device/<device_id>/activation", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:send_device"))
def create_device_activation(device_id: str) -> Response:
    """---
    post:
      summary: Create a device activation
      description: >-
        Create a new activation for a known device. Responds with an activation
        code, to be used once to validate the activation.
      tags: [device-auth]
      parameters:
        - name: device_id
          in: path
          required: true
          description: The UUID of the device for which to create an activation
          schema:
            type: string
            example: cc71c130-dbc8-4961-a462-a491523a9f8c
      responses:
        '200':
          description: object containing the code and expiry time
          content:
            application/json:
              schema: DeviceActivationResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return jsonify(controller.create_device_activation(device_id))


# This endpoint is is protected by an authorisation code, not a JWT
@api_blueprint.route("/dhos/v1/device/<device_id>/jwt", methods=["GET"])
def get_device_jwt(device_id: str) -> Response:
    """---
    get:
      summary: Get a JWT for a device
      description: >-
        Responds with a valid device JWT. Requires the `x-authorisation-code`
        header containing a code acquired by validating a device activation.
      tags: [device-auth]
      parameters:
        - name: device_id
          in: path
          required: true
          description: UUID of the device
          schema:
            type: string
            example: ab3d9aa3-d5aa-406a-87b2-cd67ad872724
        - name: x-authorisation-code
          in: header
          description: An authorisation header
          required: true
          schema:
            type: string
            example: swe87ftys78eftse87tf
      responses:
        '200':
          description: A structure containing a valid device JWT
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JwtResponse'
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    auth_code = request.headers.get("x-authorisation-code", None)
    if auth_code is None:
        raise ValueError("Request header should contain auth_code")
    return jsonify(controller.get_device_jwt(device_id, auth_code))


@api_blueprint.route("/dhos/v1/device", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:send_device"))
def get_devices() -> Response:
    """---
    get:
      summary: Get a list of devices
      description: >-
        Responds with a list of known devices, containing details such as
        location and name.
      tags: [device-auth]
      parameters:
        - name: location_id
          in: query
          required: false
          description: 'UUID of a location, for filtering the device list'
          schema:
            type: string
            example: 2c4f1d24-2952-4d4e-b1d1-3637e33cc161
        - name: active
          in: query
          required: false
          description: Whether to filter by active/inactive devices
          schema:
            type: boolean
            example: true
      responses:
        '200':
          description: A list of devices
          content:
            application/json:
              schema:
                type: array
                items: Device
        default:
          description: >-
              Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    if request.is_json:
        raise ValueError("Request should not contain a JSON body")
    device_type: Optional[str] = request.args.get("type", None)
    active: bool = RequestArg.active(default="true")
    location_id: Optional[str] = RequestArg.string("location_id", default=None)
    return jsonify(controller.get_devices(device_type, active, location_id))


# SHARED


# This endpoint is protected by a one-time PIN, not a JWT
@api_blueprint.route("/dhos/v1/activation/<activation_code>", methods=["POST"])
def validate_activation(activation_code: str) -> Response:
    """---
    post:
      summary: Validate an activation
      description: >-
        Validate ('activate') a previously-created activation for a patient or
        device. Requires the one-time-PIN (OTP) provided when the activation was
        created. Responds with a valid authorisation code to be used to retrieve
        a JWT.
      tags: [activation]
      parameters:
        - name: activation_code
          in: path
          required: true
          description: the activation code associated with the device
          schema:
            type: string
            example: 45f234jfg634hjg6
        - name: type
          in: query
          required: false
          description: The device type
          schema:
            type: string
            example: send_entry
      requestBody:
        description: The one time PIN that confirms the activation
        required: false
        content:
          application/json:
            schema:
              oneOf:
                - $ref: '#/components/schemas/AuthorisationRequest'
      responses:
        '200':
          description: Object containing the code and expiry time
          content:
            application/json:
              schema:
                oneOf:
                  - $ref: '#/components/schemas/ValidateDeviceActivationResponse'
                  - $ref: '#/components/schemas/ValidatePatientActivationResponse'
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    device_type: Optional[str] = request.args.get("type", None)
    if not device_type or device_type == "gdm":
        _json = schema.post(required={"otp": str})
        return jsonify(
            controller.update_patient_activation(activation_code, _json["otp"])
        )
    elif device_type == "send_entry":
        return jsonify(
            controller.update_device_activation(activation_code, device_type)
        )
    raise ValueError(f"Invalid device type: {device_type}")

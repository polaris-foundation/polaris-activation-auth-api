import codecs
import subprocess

import sadisplay

from dhos_activation_auth_api.models import (
    clinician,
    device,
    device_activation,
    group,
    patient,
    patient_activation,
    product,
)

desc = sadisplay.describe(
    [
        clinician.Clinician,
        device.Device,
        device_activation.DeviceActivation,
        group.Group,
        patient.Patient,
        patient_activation.PatientActivation,
        product.Product,
    ]
)
with codecs.open("docs/schema.plantuml", "w", encoding="utf-8") as f:
    f.write(sadisplay.plantuml(desc).rstrip() + "\n")

with codecs.open("docs/schema.dot", "w", encoding="utf-8") as f:
    f.write(sadisplay.dot(desc).rstrip() + "\n")

my_cmd = ["dot", "-Tpng", "docs/schema.dot"]
with open("docs/schema.png", "w") as outfile:
    subprocess.run(my_cmd, stdout=outfile)

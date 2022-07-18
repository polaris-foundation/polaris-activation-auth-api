Feature: Activate devices
    As an administrator
    I want to activate devices
    So that they can use SEND Entry

    Background:
        Given I have a valid JWT
        And I am a known clinician
        And a device exists

    Scenario: Device update
        When I update the device
        Then a "SEND entry device update" AUDIT_MESSAGE message is published to RabbitMQ
        And I can get the device details
        And I see the device details have been updated

    Scenario: Create a device activation code
        When I request a device activation code
        And I validate the device activation using the code
        Then I receive a device authorisation code
        And I can use the code to generate a valid device JWT
        And a "SEND entry device auth success" AUDIT_MESSAGE message is published to RabbitMQ
        And I can use the device JWT to generate a valid clinician JWT
        And a "SEND entry login success" AUDIT_MESSAGE message is published to RabbitMQ

    Scenario: Inactive device can't obtain activation code
        When I deactivate the device
        Then a "SEND entry device update" AUDIT_MESSAGE message is published to RabbitMQ
        When I request a device activation code
        And I validate the device activation using the code
        Then I receive a device authorisation code
        But I can not use the code to generate a valid device JWT
        And a "SEND entry device auth failed" AUDIT_MESSAGE message is published to RabbitMQ
 

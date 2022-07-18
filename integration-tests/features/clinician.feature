Feature: Clinician management
    As an administrator
    I want to manage clinicians
    So that I can control their access to SEND Entry

    Background:
        Given I have a valid JWT
        And I am a known clinician
 

    Scenario: Inactive clinician can't obtain JWT
        Given a device exists
        When I deactivate the clinician
        And I request a device activation code
        And I validate the device activation using the code
        Then I receive a device authorisation code
        And I can use the code to generate a valid device JWT
        And a "SEND entry device auth success" AUDIT_MESSAGE message is published to RabbitMQ
        But I can not use the device JWT to generate a valid clinician JWT
        And a "SEND entry login failure" AUDIT_MESSAGE message is published to RabbitMQ

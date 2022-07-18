Feature: Activate patients
    As a clinician
    I want to activate patients
    So that they can use the mobile app

    Background:
        Given I have a valid JWT

    Scenario: Create a patient activation code
        Given a patient record exists
        When I request a patient activation code
        Then a patient activation code is returned
        And the patient activation is stored

    Scenario: Activate a patient
        Given a patient record exists
        When I request a patient activation code
        When I validate the patient activation using the code
        Then I receive a patient authorisation code
        And I can use the code to generate a valid patient JWT

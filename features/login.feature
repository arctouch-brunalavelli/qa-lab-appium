# language: en
@login
Feature: User login
  As a mobile user
  I want to authenticate
  So that I can access the application

  # Tag @android for platform-specific CI jobs; add @ios when iOS is wired.
  @android
  Scenario: Successful login with valid credentials
    Given the app is open
    When the user fill the "Email" field with valid username "testing@arctouch.com"
    And the user fill the "Password" field with valid password "QA1234"
    And the user taps "Sign In"
    Then the user should be logged in the app
    And the application session should remain active

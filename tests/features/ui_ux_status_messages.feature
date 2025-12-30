Feature: Status Messages
  Test all status message types and formatting

  Scenario: Display info message
    Given the system needs to show information
    When an info message is displayed
    Then I should see message with format:
      """
      ℹ Loading schema from URL...
      """
    And the info symbol (ℹ) should be visible
    And the message should be on same line

  Scenario: Display success message
    Given an operation completes successfully
    When a success message is displayed
    Then I should see message with format:
      """
      ✓ Schema downloaded successfully
      """
    And the checkmark (✓) should be visible
    And the message should be clear and concise

  Scenario: Display warning message
    Given a non-critical issue occurs
    When a warning message is displayed
    Then I should see message with format:
      """
      ⚠ Warning: Schema has deprecated fields
      """
    And the warning symbol (⚠) should be visible
    And the message should explain the issue

  Scenario: Display error message
    Given a critical error occurs
    When an error message is displayed
    Then I should see message with format:
      """
      ✗ Error: Failed to connect to API
         Check your network connection and try again
      """
    And the error symbol (✗) should be visible
    And additional details should be indented
    And recovery options should be listed

  Scenario: Display multi-line success output
    Given schema is processed successfully
    When success output is displayed
    Then I should see:
      """
      ✓ Schema processed:
        - API: Weather.gov API
        - Version: 1.0.0
        - Endpoints: 24
      """
    And each detail should be indented
    And formatting should be consistent

  Scenario: Status updater maintains history
    Given a status updater is initialized
    When I update status multiple times
    Then all status updates should be in history
    And I can retrieve previous statuses



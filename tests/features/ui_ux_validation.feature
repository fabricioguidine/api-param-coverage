Feature: User Input Validation
  Ensure all user inputs are properly validated and provide clear feedback

  Scenario: Accept valid schema URL
    Given I am at the schema URL prompt
    When I enter "https://api.example.com/swagger.json"
    Then the input should be accepted
    And validation should pass

  Scenario: Reject malformed URL
    Given I am at the schema URL prompt
    When I enter "not-a-url"
    Then I should see error message "Invalid URL format"
    And I should see available options
    And cursor should remain at prompt

  Scenario: Handle empty input with default suggestion
    Given I am at the schema URL prompt
    When I press Enter without input
    Then I should see "No URL provided. Using example"
    And I should see confirmation prompt
    And I can accept or decline

  Scenario: Accept coverage percentage within range
    Given I am at coverage percentage prompt
    When I enter coverage percentage "75"
    Then the input should be accepted
    And I should see "Coverage set to: 75%"

  Scenario: Reject coverage percentage outside range
    Given I am at coverage percentage prompt
    When I enter coverage percentage "150"
    Then I should see "Invalid percentage. Using default (100%)"
    And the system should continue with default

  Scenario: Handle non-numeric coverage input
    Given I am at coverage percentage prompt
    When I enter coverage percentage "abc"
    Then I should see "Invalid input. Using default (100%)"


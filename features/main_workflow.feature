Feature: Main Workflow - API Test Scenario Generation
  As a user
  I want to generate test scenarios from Swagger schemas
  So that I can test my API endpoints with proper coverage

  Background:
    Given the system is initialized
    And I have a valid OpenAI API key configured

  Scenario: Generate test scenarios with schema URL input
    Given I provide a Swagger schema URL "https://api.weather.gov/openapi.json"
    When I run the main workflow
    And I choose to generate BRD from Swagger
    And I specify coverage percentage of "100"
    Then the schema should be downloaded successfully
    And the schema should be processed
    And the schema should be analyzed
    And a BRD should be generated
    And BRD should be validated against the schema
    And endpoints should be cross-referenced
    And Gherkin scenarios should be generated
    And CSV file should be created
    And analytics reports should be generated

  Scenario: Load existing BRD schema file
    Given I provide a Swagger schema URL "https://api.weather.gov/openapi.json"
    When I run the main workflow
    And I choose to load existing BRD schema
    And I select BRD file "weather_gov_api_brd"
    Then the BRD should be loaded successfully
    And BRD should be validated against the schema
    And endpoints should be cross-referenced
    And Gherkin scenarios should be generated

  Scenario: Parse BRD from document
    Given I provide a Swagger schema URL "https://api.weather.gov/openapi.json"
    And I have a BRD document "test_brd.txt" in the input directory
    When I run the main workflow
    And I choose to parse BRD from document
    And I select document "test_brd.txt"
    Then the BRD document should be parsed successfully
    And BRD should be validated against the schema
    And endpoints should be cross-referenced

  Scenario: Generate test scenarios with custom coverage percentage
    Given I provide a Swagger schema URL "https://api.weather.gov/openapi.json"
    When I run the main workflow
    And I choose to generate BRD from Swagger
    And I specify coverage percentage of "50"
    Then the BRD should cover approximately "50" percent of endpoints
    And only covered endpoints should be tested

  Scenario: Handle missing API key gracefully
    Given I do not have a valid OpenAI API key configured
    When I run the main workflow
    Then the system should display an error message
    And the workflow should exit gracefully

  Scenario: Handle invalid schema URL
    Given I provide an invalid Swagger schema URL "https://invalid-url.com/schema.json"
    When I run the main workflow
    Then the system should display an error message
    And the workflow should exit gracefully

  Scenario: Handle empty URL input
    Given I provide an empty schema URL
    When I run the main workflow
    Then the system should display an error message
    And the workflow should exit gracefully


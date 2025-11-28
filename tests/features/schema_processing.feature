Feature: Schema Processing
  As a developer
  I want to process and analyze Swagger schemas
  So that I can understand the API structure

  Background:
    Given the system is initialized

  Scenario: Download and validate Swagger 2.0 schema
    Given I have a Swagger 2.0 schema URL
    When I download the schema for processing
    Then the schema should be downloaded successfully
    And the schema format should be detected as "Swagger 2.0"
    And the schema should be saved to the schemas directory

  Scenario: Download and validate OpenAPI 3.0 schema
    Given I have an OpenAPI 3.0 schema URL
    When I download the schema for processing
    Then the schema should be downloaded successfully
    And the schema format should be detected as "OpenAPI 3.0"
    And the schema should be saved to the schemas directory

  Scenario: Process schema and extract endpoints
    Given I have a downloaded schema file
    When I process the schema
    Then the schema should be processed successfully
    And endpoints should be extracted
    And endpoint count should be greater than zero

  Scenario: Analyze schema for test traceability
    Given I have a processed schema
    When I analyze the schema
    Then the analysis should complete successfully
    And complexity metrics should be calculated
    And parameter information should be extracted



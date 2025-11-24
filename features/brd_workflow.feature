Feature: BRD Workflow
  As a tester
  I want to work with Business Requirement Documents
  So that I can scope my API testing

  Background:
    Given the system is initialized
    And I have a processed Swagger schema

  Scenario: Generate BRD from Swagger with full coverage
    Given I have a Swagger schema with multiple endpoints
    When I generate a BRD from the Swagger schema
    And I specify coverage percentage of "100"
    Then a BRD should be created
    And the BRD should contain requirements for all endpoints
    And the BRD should be saved to the output directory

  Scenario: Generate BRD from Swagger with partial coverage
    Given I have a Swagger schema with multiple endpoints
    When I generate a BRD from the Swagger schema
    And I specify coverage percentage of "50"
    Then a BRD should be created
    And the BRD should prioritize critical endpoints
    And the BRD should cover approximately "50" percent of endpoints

  Scenario: Validate BRD against Swagger schema
    Given I have a BRD schema
    And I have a Swagger schema
    When I validate the BRD against the Swagger schema
    Then validation should complete
    And orphaned endpoints should be identified
    And missing endpoints should be identified
    And a validation report should be generated

  Scenario: Cross-reference BRD with Swagger
    Given I have a BRD schema
    And I have a Swagger schema analysis
    When I cross-reference the BRD with the Swagger schema
    Then endpoints should be filtered by BRD coverage
    And coverage percentage should be calculated
    And a coverage report should be generated

  Scenario: Load BRD from file
    Given I have a BRD schema file in the output directory
    When I load the BRD from file
    Then the BRD should be loaded successfully
    And the BRD structure should be valid
    And requirements should be accessible

  Scenario: Parse BRD from text document
    Given I have a BRD text document
    When I parse the BRD document
    Then the document should be parsed successfully
    And a BRD schema should be created
    And requirements should be extracted


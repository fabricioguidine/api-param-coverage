Feature: Interactive Selection Menus
  Test all interactive menus for proper display and navigation

  Scenario: Display BRD options menu
    Given I reach the BRD handling step
    Then I should see menu with 3 numbered options
    And each option should be clearly described
    And I should see "Select option [1-3]:" prompt
    And cursor should be positioned after prompt

  Scenario: Select valid menu option
    Given I see the BRD options menu
    When I enter menu choice "1"
    Then option 1 should be selected
    And the next step should proceed

  Scenario: Reject invalid menu option
    Given I see the BRD options menu
    When I enter menu choice "5"
    Then I should see error "Invalid option. Please select 1-3"
    And the menu should be redisplayed
    And cursor should remain at prompt

  Scenario: Handle letter input in menu
    Given I see the BRD options menu
    When I enter menu choice "a"
    Then I should see error "Invalid input. Enter a number"
    And the menu should be redisplayed

  Scenario: Navigate file selection menu
    Given I see file selection menu with 5 files
    When I select option "2"
    Then file 2 should be selected
    And I should see the selected file name

  Scenario: Cancel from selection menu
    Given I see file selection menu with cancel option
    When I select the cancel option
    Then I should return to previous menu
    And no file should be selected

  Scenario: Handle empty list in selection
    Given I see a selection menu
    When the list is empty
    Then I should see "No items available for selection"
    And selection should return None


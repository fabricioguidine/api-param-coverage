Feature: Progress Indicators
  Test all progress bars and status updates

  Scenario: Display progress bar during download
    Given schema download is in progress
    When progress reaches 50%
    Then I should see progress bar with format:
      """
      Downloading: [==========----------] 50% (1024KB/2048KB) ETA: 2.5s
      """
    And the bar should update in real-time
    And ETA should be reasonably accurate

  Scenario: Display processing progress
    Given schema analysis is in progress
    When processing endpoint 12 of 24
    Then I should see:
      """
      Analyzing: [===========---------] 50% (12/24) | Current: /api/users
      """
    And current endpoint should be shown
    And percentage should be accurate

  Scenario: Display chunk progress for LLM
    Given LLM is processing 2 chunks
    When chunk 1 is complete
    Then I should see:
      """
      Chunk 1/2: [====================] 100% (12/12) ✓
      Chunk 2/2: [=====---------------] 25% (3/12) | Tokens: 756/3000
      """
    And token usage should be displayed
    And completed chunks should show checkmark

  Scenario: Handle progress bar completion
    Given a progress bar is at 100%
    Then the bar should show:
      """
      Complete: [====================] 100% (24/24) ✓
      """
    And cursor should move to next line
    And subsequent output should not overlap

  Scenario: Display progress with status message
    Given a progress bar is active
    When I update progress with status "Processing endpoint /api/users"
    Then I should see the status message in the progress bar
    And the progress percentage should be visible



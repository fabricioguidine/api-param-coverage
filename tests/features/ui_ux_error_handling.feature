Feature: Error Handling and Recovery
  Test error scenarios and recovery options

  Scenario: Handle network timeout gracefully
    Given schema download times out
    When an error occurs
    Then I should see:
      """
      ✗ Error: Connection timeout
         The server is not responding
      
      Recovery options:
        1. Retry download
        2. Use different URL
        3. Exit
      
      Select option [1-3]: _
      """
    And I should be able to select recovery option
    And the workflow should continue based on selection

  Scenario: Handle keyboard interrupt
    Given a long operation is in progress
    When I press Ctrl+C
    Then I should see:
      """
      
      ⚠️  Process interrupted by user
      
      State has been saved. You can resume later.
      """
    And the application should exit gracefully
    And no corrupted files should be left

  Scenario: Handle missing required dependency
    Given PyPDF2 is not installed
    When I try to parse a PDF document
    Then I should see:
      """
      ✗ Error: Required dependency not installed
         PDF parsing requires PyPDF2
      
      Install with: pip install PyPDF2
      
      Recovery options:
        1. Continue without PDF parsing
        2. Exit and install dependency
      
      Select option [1-2]: _
      """

  Scenario: Handle API key missing
    Given LLM_API_KEY is not set
    When the application starts
    Then I should see:
      """
      ✗ Error: LLM API key not configured
      
      Please create a .env file with:
        LLM_API_KEY=your-api-key-here
      
      Supported providers:
        • Groq: gsk_... → llama-3.1-70b-versatile
        • OpenAI: sk-... → gpt-4
        • Anthropic: sk-ant-... → claude-3-sonnet
        • Google: AIza... → gemini-pro
        • Azure: api-... → gpt-4
      
      Press Enter to exit and configure...
      """
    And application should not proceed without key

  Scenario: Handle disk full error
    Given disk space is exhausted
    When trying to save CSV file
    Then I should see:
      """
      ✗ Error: No space left on device
         Cannot save output file
      
      Recovery options:
        1. Free up space and retry
        2. Change output directory
        3. Exit without saving
      
      Select option [1-3]: _
      """
    And I should be able to select alternative location

  Scenario: Error handler provides default options
    Given an error occurs without custom recovery options
    When error handler is invoked
    Then I should see default recovery options:
      """
      Options:
        1. Retry
        2. Continue
        3. Exit
      """
    And I can select any of these options



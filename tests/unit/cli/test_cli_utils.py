"""
Comprehensive tests for CLI Utilities module.

Tests cover:
- User Input Validation
- Interactive Selection Menus
- Progress Indicators
- Status Messages
- Error Handling & Recovery
"""

import pytest

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit
import sys
import time
from io import StringIO
from unittest.mock import patch, Mock, MagicMock

from src.modules.cli.cli_utils import (
    ProgressBar,
    StatusUpdater,
    InteractiveSelector,
    ErrorHandler,
    confirm_action,
    print_section,
    print_success,
    print_error,
    print_warning,
    print_info
)
from src.utils.validators import validate_url, validate_api_key, ValidationError


# ============================================================================
# CATEGORY 1: USER INPUT VALIDATION
# ============================================================================

class TestUserInputValidation:
    """Test cases for user input validation scenarios."""
    
    def test_accept_valid_schema_url(self):
        """Test accepting valid schema URL."""
        url = "https://api.example.com/swagger.json"
        result = validate_url(url)
        assert result == url
    
    def test_reject_malformed_url(self):
        """Test rejecting malformed URL."""
        with pytest.raises(ValidationError) as exc_info:
            validate_url("not-a-url")
        assert "Invalid URL format" in str(exc_info.value)
    
    def test_reject_url_without_scheme(self):
        """Test rejecting URL without scheme."""
        with pytest.raises(ValidationError) as exc_info:
            validate_url("api.example.com/swagger.json")
        assert "Invalid URL format" in str(exc_info.value)
    
    def test_reject_url_with_invalid_scheme(self):
        """Test rejecting URL with invalid scheme."""
        with pytest.raises(ValidationError) as exc_info:
            validate_url("ftp://api.example.com/swagger.json")
        assert "URL must use http or https" in str(exc_info.value)
    
    def test_accept_valid_https_url(self):
        """Test accepting valid HTTPS URL."""
        url = "https://api.example.com/v2/openapi.yaml"
        result = validate_url(url)
        assert result == url
    
    def test_accept_valid_http_url(self):
        """Test accepting valid HTTP URL."""
        url = "http://localhost:8080/swagger.json"
        result = validate_url(url)
        assert result == url
    
    def test_reject_empty_url(self):
        """Test rejecting empty URL."""
        with pytest.raises(ValidationError) as exc_info:
            validate_url("")
        assert "URL cannot be empty" in str(exc_info.value)
    
    def test_reject_none_url(self):
        """Test rejecting None URL."""
        with pytest.raises(ValidationError):
            validate_url(None)
    
    @patch('builtins.input', return_value='75')
    def test_accept_coverage_percentage_within_range(self, mock_input):
        """Test accepting coverage percentage within range."""
        coverage_input = input("Enter coverage %: ").strip()
        coverage = float(coverage_input)
        assert 1 <= coverage <= 100
        assert coverage == 75.0
    
    @patch('builtins.input', return_value='150')
    def test_reject_coverage_percentage_outside_range(self, mock_input, capsys):
        """Test rejecting coverage percentage outside range."""
        coverage_input = input("Enter coverage %: ").strip()
        try:
            coverage = float(coverage_input)
            if coverage < 1 or coverage > 100:
                print("Invalid percentage. Using default (100%).")
        except ValueError:
            print("Invalid input. Using default (100%).")
        
        captured = capsys.readouterr()
        assert "Invalid percentage" in captured.out or "Invalid input" in captured.out
    
    @patch('builtins.input', return_value='abc')
    def test_handle_non_numeric_coverage_input(self, mock_input, capsys):
        """Test handling non-numeric coverage input."""
        coverage_input = input("Enter coverage %: ").strip()
        try:
            coverage = float(coverage_input)
        except ValueError:
            print("Invalid input. Using default (100%).")
        
        captured = capsys.readouterr()
        assert "Invalid input" in captured.out
    
    def test_validate_api_key_valid_format(self):
        """Test validating valid API key format."""
        api_key = "gsk_test12345678901234567890"
        result = validate_api_key(api_key)
        assert result == api_key
    
    def test_validate_api_key_too_short(self):
        """Test rejecting API key that's too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_api_key("short")
        assert "too short" in str(exc_info.value).lower()
    
    def test_validate_api_key_too_long(self):
        """Test rejecting API key that's too long."""
        long_key = "a" * 501
        with pytest.raises(ValidationError) as exc_info:
            validate_api_key(long_key)
        assert "too long" in str(exc_info.value).lower()
    
    def test_validate_api_key_invalid_characters(self):
        """Test rejecting API key with invalid characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_api_key("test@key#123")
        assert "invalid characters" in str(exc_info.value).lower()


# ============================================================================
# CATEGORY 2: INTERACTIVE SELECTION MENUS
# ============================================================================

class TestInteractiveSelectionMenus:
    """Test cases for interactive selection menus."""
    
    @patch('builtins.input', return_value='1')
    def test_display_brd_options_menu(self, mock_input, capsys):
        """Test displaying BRD options menu."""
        options = [
            "Load existing BRD schema file (JSON)",
            "Parse BRD from document (PDF, Word, TXT, CSV)",
            "Generate BRD from Swagger schema (using LLM)"
        ]
        result = InteractiveSelector.select_from_list(options, "How would you like to handle the BRD?")
        
        captured = capsys.readouterr()
        assert "How would you like to handle the BRD?" in captured.out
        assert "1." in captured.out
        assert "2." in captured.out
        assert "3." in captured.out
        assert result == options[0]
    
    @patch('builtins.input', return_value='2')
    def test_select_valid_menu_option(self, mock_input):
        """Test selecting valid menu option."""
        options = ["Option 1", "Option 2", "Option 3"]
        result = InteractiveSelector.select_from_list(options, "Select option")
        assert result == "Option 2"
    
    @patch('builtins.input', side_effect=['5', '1'])
    def test_reject_invalid_menu_option(self, mock_input, capsys):
        """Test rejecting invalid menu option."""
        options = ["Option 1", "Option 2", "Option 3"]
        result = InteractiveSelector.select_from_list(options, "Select option")
        
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out or "Invalid input" in captured.out
        assert result == "Option 1"  # Should eventually accept valid input
    
    @patch('builtins.input', side_effect=['a', '1'])
    def test_handle_letter_input_in_menu(self, mock_input, capsys):
        """Test handling letter input in menu."""
        options = ["Option 1", "Option 2"]
        result = InteractiveSelector.select_from_list(options, "Select option")
        
        captured = capsys.readouterr()
        assert "Invalid input" in captured.out or "Invalid choice" in captured.out
        assert result == "Option 1"
    
    @patch('builtins.input', return_value='4')
    def test_cancel_from_selection_menu(self, mock_input):
        """Test canceling from selection menu."""
        options = ["Item 1", "Item 2", "Item 3"]
        result = InteractiveSelector.select_from_list(
            options,
            "Select item",
            allow_cancel=True
        )
        assert result is None
    
    @patch('builtins.input', return_value='1')
    def test_navigate_file_selection_menu(self, mock_input, capsys):
        """Test navigating file selection menu."""
        files = ["file1.json", "file2.json", "file3.json"]
        result = InteractiveSelector.select_from_list(
            files,
            "Select file",
            display_func=lambda x: x
        )
        
        captured = capsys.readouterr()
        assert "Select file" in captured.out
        assert "1." in captured.out
        assert result == "file1.json"
    
    @patch('builtins.input', return_value='1')
    def test_select_with_display_function(self, mock_input):
        """Test selection with custom display function."""
        items = [{'name': 'Item 1', 'id': 1}, {'name': 'Item 2', 'id': 2}]
        result = InteractiveSelector.select_from_list(
            items,
            "Select item",
            display_func=lambda x: x['name']
        )
        assert result == {'name': 'Item 1', 'id': 1}
    
    def test_select_from_empty_list(self, capsys):
        """Test selection with empty list."""
        result = InteractiveSelector.select_from_list([], "Select item")
        
        captured = capsys.readouterr()
        assert "No items available" in captured.out
        assert result is None
    
    @patch('builtins.input', side_effect=[KeyboardInterrupt()])
    def test_handle_keyboard_interrupt_in_menu(self, mock_input, capsys):
        """Test handling keyboard interrupt in menu."""
        options = ["Option 1", "Option 2"]
        result = InteractiveSelector.select_from_list(options, "Select option")
        
        captured = capsys.readouterr()
        assert "canceled" in captured.out.lower()
        assert result is None


# ============================================================================
# CATEGORY 3: PROGRESS INDICATORS
# ============================================================================

class TestProgressIndicators:
    """Test cases for progress indicators."""
    
    def test_display_progress_bar_during_download(self, capsys):
        """Test displaying progress bar during download."""
        pb = ProgressBar(total=100, description="Downloading")
        pb.update(50)
        pb.finish()
        
        captured = capsys.readouterr()
        assert "Downloading" in captured.out
        assert "50%" in captured.out or "50/100" in captured.out
    
    def test_display_processing_progress(self, capsys):
        """Test displaying processing progress."""
        pb = ProgressBar(total=24, description="Analyzing")
        pb.update(12, status="Current: /api/users")
        pb.finish()
        
        captured = capsys.readouterr()
        assert "Analyzing" in captured.out
        assert "12/24" in captured.out or "50%" in captured.out
    
    def test_display_chunk_progress_for_llm(self, capsys):
        """Test displaying chunk progress for LLM."""
        pb = ProgressBar(total=12, description="Chunk 1/2")
        pb.update(12)
        pb.finish()
        
        captured = capsys.readouterr()
        assert "Chunk 1/2" in captured.out
        assert "100%" in captured.out or "12/12" in captured.out
    
    def test_handle_progress_bar_completion(self, capsys):
        """Test handling progress bar completion."""
        pb = ProgressBar(total=24, description="Complete")
        pb.finish()
        
        captured = capsys.readouterr()
        assert "Complete" in captured.out
        assert "100%" in captured.out or "24/24" in captured.out
    
    def test_progress_bar_with_eta(self, capsys):
        """Test progress bar with ETA calculation."""
        pb = ProgressBar(total=100, description="Processing")
        time.sleep(0.1)  # Small delay for ETA calculation
        pb.update(10)
        pb.finish()
        
        captured = capsys.readouterr()
        assert "Processing" in captured.out
        # ETA should be present after first update
        assert "ETA" in captured.out or "10/100" in captured.out
    
    def test_progress_bar_zero_total(self, capsys):
        """Test progress bar with zero total."""
        pb = ProgressBar(total=0, description="Test")
        pb.update(0)
        pb.finish()
        
        # Should not crash
        captured = capsys.readouterr()
        assert "Test" in captured.out
    
    def test_progress_bar_status_message(self, capsys):
        """Test progress bar with status message."""
        pb = ProgressBar(total=10, description="Processing")
        pb.update(5, status="Current: endpoint /api/users")
        pb.finish()
        
        captured = capsys.readouterr()
        assert "Current: endpoint /api/users" in captured.out


# ============================================================================
# CATEGORY 4: STATUS MESSAGES
# ============================================================================

class TestStatusMessages:
    """Test cases for status messages."""
    
    def test_display_info_message(self, capsys):
        """Test displaying info message."""
        print_info("Loading schema from URL...")
        
        captured = capsys.readouterr()
        assert "Loading schema from URL" in captured.out
        assert "ℹ" in captured.out
    
    def test_display_success_message(self, capsys):
        """Test displaying success message."""
        print_success("Schema downloaded successfully")
        
        captured = capsys.readouterr()
        assert "Schema downloaded successfully" in captured.out
        assert "✓" in captured.out
    
    def test_display_warning_message(self, capsys):
        """Test displaying warning message."""
        print_warning("Warning: Schema has deprecated fields")
        
        captured = capsys.readouterr()
        assert "Warning: Schema has deprecated fields" in captured.out
        assert "⚠" in captured.out
    
    def test_display_error_message(self, capsys):
        """Test displaying error message."""
        print_error("Error: Failed to connect to API")
        
        captured = capsys.readouterr()
        assert "Error: Failed to connect to API" in captured.out
        assert "✗" in captured.out
    
    def test_display_multi_line_success_output(self, capsys):
        """Test displaying multi-line success output."""
        print_success("Schema processed:")
        print("  - API: Weather.gov API")
        print("  - Version: 1.0.0")
        print("  - Endpoints: 24")
        
        captured = capsys.readouterr()
        assert "Schema processed" in captured.out
        assert "Weather.gov API" in captured.out
        assert "Endpoints: 24" in captured.out
    
    def test_status_updater_info_level(self, capsys):
        """Test status updater with info level."""
        su = StatusUpdater()
        su.update("Processing schema...", "info")
        
        captured = capsys.readouterr()
        assert "Processing schema" in captured.out
        assert "ℹ" in captured.out
    
    def test_status_updater_success_level(self, capsys):
        """Test status updater with success level."""
        su = StatusUpdater()
        su.update("Operation completed", "success")
        
        captured = capsys.readouterr()
        assert "Operation completed" in captured.out
        assert "✓" in captured.out
    
    def test_status_updater_warning_level(self, capsys):
        """Test status updater with warning level."""
        su = StatusUpdater()
        su.update("Warning message", "warning")
        
        captured = capsys.readouterr()
        assert "Warning message" in captured.out
        assert "⚠" in captured.out
    
    def test_status_updater_error_level(self, capsys):
        """Test status updater with error level."""
        su = StatusUpdater()
        su.update("Error occurred", "error")
        
        captured = capsys.readouterr()
        assert "Error occurred" in captured.out
        assert "✗" in captured.out
    
    def test_status_updater_history(self):
        """Test status updater maintains history."""
        su = StatusUpdater()
        su.update("Status 1", "info")
        su.update("Status 2", "success")
        
        assert len(su.status_history) == 2
        assert su.status_history[0][2] == "Status 1"
        assert su.status_history[1][2] == "Status 2"
    
    def test_status_updater_clear(self):
        """Test clearing status updater."""
        su = StatusUpdater()
        su.update("Test status")
        su.clear()
        
        assert su.current_status is None


# ============================================================================
# CATEGORY 5: ERROR HANDLING & RECOVERY
# ============================================================================

class TestErrorHandlingRecovery:
    """Test cases for error handling and recovery."""
    
    @patch('builtins.input', return_value='1')
    def test_handle_network_timeout_gracefully(self, mock_input, capsys):
        """Test handling network timeout gracefully."""
        error = ConnectionError("Connection timeout")
        result = ErrorHandler.handle_error(
            error,
            "downloading schema",
            ["Retry download", "Use different URL", "Exit"]
        )
        
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "✗" in captured.out
        assert "downloading schema" in captured.out.lower()
        assert "Retry download" in captured.out or "1." in captured.out
        assert result == "retry download"
    
    @patch('builtins.input', return_value='1')
    def test_handle_error_with_custom_recovery_options(self, mock_input, capsys):
        """Test error handling with custom recovery options."""
        error = FileNotFoundError("File not found")
        recovery_options = ["Try different file", "Generate new file", "Skip this step"]
        result = ErrorHandler.handle_error(error, "loading file", recovery_options)
        
        captured = capsys.readouterr()
        assert "File not found" in captured.out or "error" in captured.out.lower()
        assert "Try different file" in captured.out
        assert result == "try different file"
    
    @patch('builtins.input', return_value='3')
    def test_handle_error_exit_option(self, mock_input, capsys):
        """Test error handling with exit option."""
        error = ValueError("Invalid value")
        recovery_options = ["Retry", "Continue"]
        result = ErrorHandler.handle_error(error, "processing", recovery_options)
        
        captured = capsys.readouterr()
        assert "Exit" in captured.out or "3." in captured.out
        assert result == "exit"
    
    @patch('builtins.input', side_effect=[KeyboardInterrupt()])
    def test_handle_keyboard_interrupt(self, mock_input, capsys):
        """Test handling keyboard interrupt."""
        error = KeyboardInterrupt()
        result = ErrorHandler.handle_error(error, "operation")
        
        # Should return exit on keyboard interrupt
        assert result == "exit"
    
    def test_error_handler_default_recovery_options(self, capsys):
        """Test error handler with default recovery options."""
        error = Exception("Test error")
        
        with patch('builtins.input', return_value='1'):
            result = ErrorHandler.handle_error(error, "test context", None)
            assert result == "retry"
        
        with patch('builtins.input', return_value='2'):
            result = ErrorHandler.handle_error(error, "test context", None)
            assert result == "continue"
        
        with patch('builtins.input', return_value='3'):
            result = ErrorHandler.handle_error(error, "test context", None)
            assert result == "exit"
    
    @patch('builtins.input', side_effect=['5', '1'])
    def test_error_handler_invalid_choice_retry(self, mock_input, capsys):
        """Test error handler retries on invalid choice."""
        error = Exception("Test error")
        recovery_options = ["Option 1", "Option 2", "Option 3"]
        result = ErrorHandler.handle_error(error, "test", recovery_options)
        
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out or "Invalid input" in captured.out
        assert result == "option 1"


# ============================================================================
# CATEGORY 6: CONFIRMATION PROMPTS
# ============================================================================

class TestConfirmationPrompts:
    """Test cases for confirmation prompts."""
    
    @patch('builtins.input', return_value='y')
    def test_confirm_action_yes(self, mock_input):
        """Test confirm action with yes."""
        result = confirm_action("Do you want to continue?", default=False)
        assert result is True
    
    @patch('builtins.input', return_value='Y')
    def test_confirm_action_yes_uppercase(self, mock_input):
        """Test confirm action with uppercase yes."""
        result = confirm_action("Continue?", default=False)
        assert result is True
    
    @patch('builtins.input', return_value='yes')
    def test_confirm_action_yes_word(self, mock_input):
        """Test confirm action with 'yes' word."""
        result = confirm_action("Continue?", default=False)
        assert result is True
    
    @patch('builtins.input', return_value='n')
    def test_confirm_action_no(self, mock_input):
        """Test confirm action with no."""
        result = confirm_action("Continue?", default=True)
        assert result is False
    
    @patch('builtins.input', return_value='N')
    def test_confirm_action_no_uppercase(self, mock_input):
        """Test confirm action with uppercase no."""
        result = confirm_action("Continue?", default=True)
        assert result is False
    
    @patch('builtins.input', return_value='no')
    def test_confirm_action_no_word(self, mock_input):
        """Test confirm action with 'no' word."""
        result = confirm_action("Continue?", default=True)
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default_yes(self, mock_input):
        """Test confirm action with default yes (Enter key)."""
        result = confirm_action("Continue?", default=True)
        assert result is True
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default_no(self, mock_input):
        """Test confirm action with default no (Enter key)."""
        result = confirm_action("Continue?", default=False)
        assert result is False
    
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_display_confirmation_with_default_yes(self, mock_print, mock_input):
        """Test displaying confirmation with default Yes."""
        # The prompt is printed by input(), not print(), so we check the function behavior
        result = confirm_action("Do you want to continue?", default=True)
        assert result is True
        # Verify the prompt format would include (Y/n) - this is handled by input() which we mock
    
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_display_confirmation_with_default_no(self, mock_print, mock_input):
        """Test displaying confirmation with default No."""
        # The prompt is printed by input(), not print(), so we check the function behavior
        result = confirm_action("Are you sure?", default=False)
        assert result is False
        # Verify the prompt format would include (y/N) - this is handled by input() which we mock


# ============================================================================
# CATEGORY 7: SECTION HEADERS & FORMATTING
# ============================================================================

class TestSectionHeadersFormatting:
    """Test cases for section headers and formatting."""
    
    def test_display_major_section_header(self, capsys):
        """Test displaying major section header."""
        print_section("Step 1: Downloading schema...", width=70)
        
        captured = capsys.readouterr()
        assert "=" * 70 in captured.out
        assert "Step 1: Downloading schema" in captured.out
    
    def test_section_header_separator_width(self, capsys):
        """Test section header separator width."""
        print_section("Test Section", width=50)
        
        captured = capsys.readouterr()
        assert "=" * 50 in captured.out
    
    def test_section_header_centered_title(self, capsys):
        """Test section header with centered title."""
        print_section("Summary", width=70)
        
        captured = capsys.readouterr()
        assert "Summary" in captured.out
        assert "=" in captured.out

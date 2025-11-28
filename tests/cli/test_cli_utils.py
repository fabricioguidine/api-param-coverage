"""
Tests for the CLI Utilities module.
"""

import pytest
import sys
from io import StringIO
from unittest.mock import patch, Mock

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


class TestProgressBar:
    """Test cases for ProgressBar class."""
    
    def test_progress_bar_initialization(self):
        """Test ProgressBar initialization."""
        pb = ProgressBar(total=100, description="Test", width=50)
        assert pb.total == 100
        assert pb.current == 0
        assert pb.description == "Test"
        assert pb.width == 50
    
    def test_progress_bar_update(self, capsys):
        """Test progress bar update."""
        pb = ProgressBar(total=10, description="Test")
        pb.update(5)
        pb.finish()
        
        captured = capsys.readouterr()
        assert "Test" in captured.out
        assert "50%" in captured.out or "5/10" in captured.out
    
    def test_progress_bar_finish(self, capsys):
        """Test progress bar finish."""
        pb = ProgressBar(total=10, description="Test")
        pb.finish("Done")
        
        captured = capsys.readouterr()
        assert "Test" in captured.out
    
    def test_progress_bar_zero_total(self, capsys):
        """Test progress bar with zero total."""
        pb = ProgressBar(total=0, description="Test")
        pb.update(0)
        pb.finish()
        
        # Should not crash
        assert True


class TestStatusUpdater:
    """Test cases for StatusUpdater class."""
    
    def test_status_updater_initialization(self):
        """Test StatusUpdater initialization."""
        su = StatusUpdater()
        assert su.current_status is None
        assert su.status_history == []
    
    def test_status_update(self, capsys):
        """Test status update."""
        su = StatusUpdater()
        su.update("Test status", "info")
        
        captured = capsys.readouterr()
        assert "Test status" in captured.out
    
    def test_status_update_levels(self, capsys):
        """Test different status levels."""
        su = StatusUpdater()
        su.update("Info", "info")
        su.update("Success", "success")
        su.update("Warning", "warning")
        su.update("Error", "error")
        
        captured = capsys.readouterr()
        assert "Info" in captured.out
        assert "Success" in captured.out
        assert "Warning" in captured.out
        assert "Error" in captured.out
    
    def test_status_clear(self):
        """Test status clear."""
        su = StatusUpdater()
        su.update("Test")
        su.clear()
        assert su.current_status is None


class TestInteractiveSelector:
    """Test cases for InteractiveSelector class."""
    
    @patch('builtins.input', return_value='1')
    def test_select_from_list(self, mock_input):
        """Test selecting from list."""
        items = ['item1', 'item2', 'item3']
        result = InteractiveSelector.select_from_list(items, "Select item")
        assert result == 'item1'
    
    @patch('builtins.input', return_value='4')
    def test_select_from_list_cancel(self, mock_input):
        """Test canceling selection."""
        items = ['item1', 'item2', 'item3']
        result = InteractiveSelector.select_from_list(items, "Select item", allow_cancel=True)
        assert result is None
    
    @patch('builtins.input', return_value='2')
    def test_select_from_list_with_display_func(self, mock_input):
        """Test selection with display function."""
        items = [{'name': 'Item 1'}, {'name': 'Item 2'}]
        result = InteractiveSelector.select_from_list(
            items,
            display_func=lambda x: x['name']
        )
        assert result == {'name': 'Item 2'}
    
    def test_select_from_list_empty(self):
        """Test selection with empty list."""
        result = InteractiveSelector.select_from_list([])
        assert result is None


class TestErrorHandler:
    """Test cases for ErrorHandler class."""
    
    @patch('builtins.input', return_value='1')
    def test_handle_error_with_recovery(self, mock_input):
        """Test error handling with recovery options."""
        error = Exception("Test error")
        recovery_options = ["Retry", "Continue", "Exit"]
        
        result = ErrorHandler.handle_error(error, "test context", recovery_options)
        assert result == "retry"
    
    @patch('builtins.input', return_value='3')
    def test_handle_error_exit(self, mock_input):
        """Test error handling with exit option."""
        error = Exception("Test error")
        
        result = ErrorHandler.handle_error(error, "test context", None, "exit")
        assert result == "exit"


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    @patch('builtins.input', return_value='y')
    def test_confirm_action_yes(self, mock_input):
        """Test confirm action with yes."""
        result = confirm_action("Test?", default=False)
        assert result is True
    
    @patch('builtins.input', return_value='n')
    def test_confirm_action_no(self, mock_input):
        """Test confirm action with no."""
        result = confirm_action("Test?", default=True)
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default(self, mock_input):
        """Test confirm action with default."""
        result = confirm_action("Test?", default=True)
        assert result is True
    
    def test_print_section(self, capsys):
        """Test print section."""
        print_section("Test Section", width=50)
        captured = capsys.readouterr()
        assert "Test Section" in captured.out
        assert "=" in captured.out
    
    def test_print_success(self, capsys):
        """Test print success."""
        print_success("Success message")
        captured = capsys.readouterr()
        assert "Success message" in captured.out
        assert "✓" in captured.out
    
    def test_print_error(self, capsys):
        """Test print error."""
        print_error("Error message")
        captured = capsys.readouterr()
        assert "Error message" in captured.out
        assert "✗" in captured.out
    
    def test_print_warning(self, capsys):
        """Test print warning."""
        print_warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning message" in captured.out
        assert "⚠" in captured.out
    
    def test_print_info(self, capsys):
        """Test print info."""
        print_info("Info message")
        captured = capsys.readouterr()
        assert "Info message" in captured.out
        assert "ℹ" in captured.out





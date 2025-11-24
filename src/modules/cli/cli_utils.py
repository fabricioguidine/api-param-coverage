"""
CLI Utilities

Provides interactive CLI features: progress bars, status updates, error recovery.
"""

import sys
import time
from typing import List, Optional, Callable, Any
from pathlib import Path


class ProgressBar:
    """Simple progress bar implementation."""
    
    def __init__(self, total: int, description: str = "Processing", width: int = 50):
        """
        Initialize progress bar.
        
        Args:
            total: Total number of items to process
            description: Description text
            width: Width of progress bar
        """
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.start_time = time.time()
    
    def update(self, n: int = 1, status: Optional[str] = None):
        """
        Update progress bar.
        
        Args:
            n: Number of items completed
            status: Optional status message
        """
        self.current = min(self.current + n, self.total)
        self._display(status)
    
    def _display(self, status: Optional[str] = None):
        """Display progress bar."""
        if self.total == 0:
            percent = 100
        else:
            percent = int((self.current / self.total) * 100)
        
        filled = int(self.width * self.current / self.total) if self.total > 0 else self.width
        bar = '=' * filled + '-' * (self.width - filled)
        
        elapsed = time.time() - self.start_time
        if self.current > 0:
            rate = self.current / elapsed
            eta = (self.total - self.current) / rate if rate > 0 else 0
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = ""
        
        status_str = f" | {status}" if status else ""
        sys.stdout.write(f"\r{self.description}: [{bar}] {percent}% ({self.current}/{self.total}) {eta_str}{status_str}")
        sys.stdout.flush()
        
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()
    
    def finish(self, message: Optional[str] = None):
        """Finish progress bar."""
        self.current = self.total
        if message:
            self._display(message)
        else:
            self._display()
        sys.stdout.write("\n")
        sys.stdout.flush()


class StatusUpdater:
    """Provides real-time status updates."""
    
    def __init__(self):
        """Initialize status updater."""
        self.current_status = None
        self.status_history = []
    
    def update(self, status: str, level: str = "info"):
        """
        Update status.
        
        Args:
            status: Status message
            level: Status level (info, success, warning, error)
        """
        self.current_status = status
        self.status_history.append((time.time(), level, status))
        
        symbols = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗"
        }
        
        symbol = symbols.get(level, "•")
        print(f"{symbol} {status}")
    
    def clear(self):
        """Clear current status."""
        self.current_status = None


class InteractiveSelector:
    """Interactive selection with validation."""
    
    @staticmethod
    def select_from_list(
        items: List[Any],
        prompt: str = "Select an item",
        display_func: Optional[Callable[[Any], str]] = None,
        allow_cancel: bool = True
    ) -> Optional[Any]:
        """
        Interactive selection from a list.
        
        Args:
            items: List of items to select from
            prompt: Prompt message
            display_func: Function to format item display (default: str())
            allow_cancel: Allow canceling selection
            
        Returns:
            Selected item or None if canceled
        """
        if not items:
            print("⚠ No items available for selection.")
            return None
        
        print(f"\n{prompt}:")
        for i, item in enumerate(items, 1):
            if display_func:
                display = display_func(item)
            else:
                display = str(item)
            print(f"  {i}. {display}")
        
        if allow_cancel:
            print(f"  {len(items) + 1}. Cancel")
        
        while True:
            try:
                choice = input(f"\nEnter choice (1-{len(items) + (1 if allow_cancel else 0)}): ").strip()
                
                if not choice:
                    continue
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(items):
                    return items[choice_num - 1]
                elif allow_cancel and choice_num == len(items) + 1:
                    return None
                else:
                    print(f"⚠ Invalid choice. Please enter a number between 1 and {len(items) + (1 if allow_cancel else 0)}.")
            except ValueError:
                print("⚠ Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\n\n⚠ Selection canceled.")
                return None
    
    @staticmethod
    def select_with_retry(
        items: List[Any],
        prompt: str = "Select an item",
        display_func: Optional[Callable[[Any], str]] = None,
        max_retries: int = 3
    ) -> Optional[Any]:
        """
        Select with retry mechanism.
        
        Args:
            items: List of items to select from
            prompt: Prompt message
            display_func: Function to format item display
            max_retries: Maximum number of retry attempts
            
        Returns:
            Selected item or None if failed
        """
        for attempt in range(max_retries):
            result = InteractiveSelector.select_from_list(items, prompt, display_func, allow_cancel=True)
            if result is not None:
                return result
            
            if attempt < max_retries - 1:
                retry = input(f"\nRetry? (y/n): ").strip().lower()
                if retry != 'y':
                    break
        
        return None


class ErrorHandler:
    """Handles errors with recovery options."""
    
    @staticmethod
    def handle_error(
        error: Exception,
        context: str = "",
        recovery_options: Optional[List[str]] = None,
        default_action: str = "exit"
    ) -> str:
        """
        Handle error with recovery options.
        
        Args:
            error: Exception that occurred
            context: Context description
            recovery_options: List of recovery option descriptions
            default_action: Default action if no recovery (exit, continue, retry)
            
        Returns:
            Selected action
        """
        print_error(f"Error {context}: {str(error)}")
        
        if recovery_options:
            print("\nRecovery options:")
            for i, option in enumerate(recovery_options, 1):
                print(f"  {i}. {option}")
            print(f"  {len(recovery_options) + 1}. Exit")
            
            while True:
                try:
                    choice = input(f"\nSelect recovery option (1-{len(recovery_options) + 1}): ").strip()
                    choice_num = int(choice)
                    
                    if 1 <= choice_num <= len(recovery_options):
                        return recovery_options[choice_num - 1].lower()
                    elif choice_num == len(recovery_options) + 1:
                        return "exit"
                    else:
                        print(f"⚠ Invalid choice.")
                except ValueError:
                    print("⚠ Invalid input.")
                except KeyboardInterrupt:
                    return "exit"
        else:
            # Default recovery options
            print("\nOptions:")
            print("  1. Retry")
            print("  2. Continue")
            print("  3. Exit")
            
            while True:
                try:
                    choice = input("\nSelect option (1-3): ").strip()
                    choice_num = int(choice)
                    
                    if choice_num == 1:
                        return "retry"
                    elif choice_num == 2:
                        return "continue"
                    elif choice_num == 3:
                        return "exit"
                    else:
                        print("⚠ Invalid choice.")
                except ValueError:
                    print("⚠ Invalid input.")
                except KeyboardInterrupt:
                    return "exit"


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Confirm an action with user.
    
    Args:
        prompt: Confirmation prompt
        default: Default value if user just presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} ({default_str}): ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']


def print_section(title: str, width: int = 70):
    """Print a section header."""
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def print_success(message: str):
    """Print success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"✗ {message}")


def print_warning(message: str):
    """Print warning message."""
    print(f"⚠ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ {message}")



"""
LLM Provider Detection and Setup

Detects LLM provider from API key format and handles initial setup.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv, set_key, find_dotenv


def detect_provider_from_key(api_key: str) -> str:
    """
    Detect LLM provider from API key format/hash.
    
    Args:
        api_key: API key string
        
    Returns:
        Provider name: 'openai', 'anthropic', 'google', 'azure', or 'unknown'
    """
    if not api_key:
        return 'unknown'
    
    api_key = api_key.strip()
    
    # OpenAI: starts with 'sk-' and is typically 51 characters
    if api_key.startswith('sk-') and len(api_key) >= 48:
        return 'openai'
    
    # Anthropic (Claude): starts with 'sk-ant-' and is longer
    if api_key.startswith('sk-ant-'):
        return 'anthropic'
    
    # Google: typically starts with specific patterns or is a long base64-like string
    if api_key.startswith('AIza') or len(api_key) > 100:
        # Check if it looks like a Google API key
        if re.match(r'^[A-Za-z0-9_-]+$', api_key) and len(api_key) > 30:
            return 'google'
    
    # Azure OpenAI: typically contains 'azure' or specific patterns
    if 'azure' in api_key.lower() or api_key.startswith('api-'):
        return 'azure'
    
    # Default to OpenAI if it looks like a standard API key
    if re.match(r'^[A-Za-z0-9_-]+$', api_key) and 20 <= len(api_key) <= 200:
        return 'openai'
    
    return 'unknown'


def get_provider_info(provider: str) -> dict:
    """
    Get information about a provider.
    
    Args:
        provider: Provider name
        
    Returns:
        Dictionary with provider information
    """
    providers = {
        'openai': {
            'name': 'OpenAI',
            'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
            'default_model': 'gpt-4',
            'env_var': 'OPENAI_API_KEY'
        },
        'anthropic': {
            'name': 'Anthropic (Claude)',
            'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
            'default_model': 'claude-3-sonnet',
            'env_var': 'ANTHROPIC_API_KEY'
        },
        'google': {
            'name': 'Google',
            'models': ['gemini-pro', 'gemini-ultra'],
            'default_model': 'gemini-pro',
            'env_var': 'GOOGLE_API_KEY'
        },
        'azure': {
            'name': 'Azure OpenAI',
            'models': ['gpt-4', 'gpt-3.5-turbo'],
            'default_model': 'gpt-4',
            'env_var': 'AZURE_OPENAI_API_KEY'
        }
    }
    
    return providers.get(provider, {
        'name': 'Unknown',
        'models': ['gpt-4'],
        'default_model': 'gpt-4',
        'env_var': 'LLM_API_KEY'
    })


def setup_api_key() -> Tuple[Optional[str], Optional[str]]:
    """
    Setup API key on first run. Prompts user for API key and detects provider.
    
    Returns:
        Tuple of (api_key, provider) or (None, None) if cancelled
    """
    env_file = Path('.env')
    
    # Check if .env exists and has API key
    if env_file.exists():
        load_dotenv()
        api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY')
        provider = os.getenv('LLM_PROVIDER', 'openai')
        
        if api_key:
            return api_key, provider
    
    # First time setup
    print("\n" + "=" * 70)
    print("First Time Setup: LLM API Key Configuration")
    print("=" * 70)
    print("\nThis tool requires an LLM API key to generate test scenarios.")
    print("Supported providers: OpenAI, Anthropic (Claude), Google, Azure OpenAI")
    print("\nThe provider will be automatically detected from your API key format.")
    
    while True:
        api_key = input("\nEnter your LLM API key: ").strip()
        
        if not api_key:
            print("⚠ API key cannot be empty.")
            if not input("Try again? (y/n): ").strip().lower().startswith('y'):
                return None, None
            continue
        
        # Detect provider
        provider = detect_provider_from_key(api_key)
        provider_info = get_provider_info(provider)
        
        print(f"\n✓ Detected provider: {provider_info['name']}")
        print(f"  Default model: {provider_info['default_model']}")
        
        # Confirm detection
        confirm = input(f"\nIs this correct? (y/n, default: y): ").strip().lower()
        if confirm and not confirm.startswith('y'):
            # Allow manual override
            print("\nAvailable providers:")
            print("1. OpenAI (gpt-4, gpt-3.5-turbo)")
            print("2. Anthropic (claude-3-opus, claude-3-sonnet)")
            print("3. Google (gemini-pro)")
            print("4. Azure OpenAI (gpt-4)")
            
            choice = input("\nSelect provider (1-4, or press Enter to use detected): ").strip()
            provider_map = {'1': 'openai', '2': 'anthropic', '3': 'google', '4': 'azure'}
            if choice in provider_map:
                provider = provider_map[choice]
                provider_info = get_provider_info(provider)
        
        # Save to .env
        try:
            env_file_path = find_dotenv() or '.env'
            
            # Create .env if it doesn't exist
            if not Path(env_file_path).exists():
                Path(env_file_path).touch()
            
            # Save API key and provider
            set_key(env_file_path, 'LLM_API_KEY', api_key)
            set_key(env_file_path, 'LLM_PROVIDER', provider)
            
            # Also set provider-specific env var for compatibility
            provider_info = get_provider_info(provider)
            if provider_info['env_var'] != 'LLM_API_KEY':
                set_key(env_file_path, provider_info['env_var'], api_key)
            
            print(f"\n✓ API key saved to .env file")
            print(f"  Provider: {provider_info['name']}")
            print(f"  This will not be asked again.")
            
            # Reload environment
            load_dotenv(override=True)
            
            return api_key, provider
            
        except Exception as e:
            print(f"✗ Error saving API key: {e}")
            print("  Please manually create a .env file with:")
            print(f"  LLM_API_KEY={api_key}")
            print(f"  LLM_PROVIDER={provider}")
            return api_key, provider


def get_api_key_and_provider() -> Tuple[Optional[str], str]:
    """
    Get API key and provider from environment or prompt for setup.
    
    Returns:
        Tuple of (api_key, provider)
    """
    # Load environment
    load_dotenv()
    
    # Try to get from environment
    api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
    provider = os.getenv('LLM_PROVIDER', 'openai')
    
    # If no API key, run setup
    if not api_key:
        api_key, provider = setup_api_key()
        if not api_key:
            return None, 'unknown'
    
    # If provider is not set but we have a key, detect it
    if api_key and provider == 'openai':
        detected = detect_provider_from_key(api_key)
        if detected != 'unknown':
            provider = detected
    
    return api_key, provider


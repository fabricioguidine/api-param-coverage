"""
env_loader.py
Centralized .env loading so tests and CLI behave consistently.

Usage:
    from common.env_loader import load_env
    load_env()
"""
from dotenv import load_dotenv
from pathlib import Path

def load_env():
    # project_root = src/common -> src -> project_root
    root = Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)

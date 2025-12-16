import os
from pathlib import Path

import platformdirs

from paper_inbox import APP_NAME

DEV_MODE = os.getenv('PAPER_INBOX_DEV', '').lower() in ('1', 'true', 'yes')
DEV_ROOT_DIR = Path(__file__).parent.parent.parent.parent / "dev"

def get_config_dir() -> Path:
    if DEV_MODE:
        config_dir = DEV_ROOT_DIR / "config"
    else:
        config_dir = platformdirs.user_config_path(APP_NAME)
    config_dir.mkdir(parents=True, exist_ok=True)    
    return config_dir

def get_data_dir() -> Path:
    if DEV_MODE:
        data_dir = DEV_ROOT_DIR / "data"
    else:
        data_dir = platformdirs.user_data_path(APP_NAME)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_log_dir() -> Path:
    if DEV_MODE:
        log_dir = DEV_ROOT_DIR / "logs"
    else:
        log_dir = platformdirs.user_log_path(APP_NAME)
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def get_config_filepath() -> Path:
    """
    Determines the platform-specific path for the config file.
    Ensures the parent directory exists.
    """
    config_filepath = get_config_dir() / "config.toml"
    return config_filepath

def get_secrets_filepath() -> Path:
    """Returns the path where client_secrets.json should be stored."""
    secrets_filepath = get_config_dir() / "client_secrets.json"
    return secrets_filepath

def get_refresh_token_filepath() -> Path:
    """Returns the path where refresh_token.json should be stored."""
    refresh_token_filepath = get_config_dir() / "token.json"
    return refresh_token_filepath

def get_database_filepath() -> Path:
    """Returns the path where the database file should be stored."""
    database_filepath = get_data_dir() / "db.sqlite3"
    return database_filepath
from __future__ import annotations

import functools
import logging
import os
import subprocess
import sys
import time
from socket import gaierror
from typing import TYPE_CHECKING

from paper_inbox.modules import config, cron
from paper_inbox.modules.const import GREEN
from paper_inbox.modules.loggers import setup_logger

if TYPE_CHECKING:
    from rich.console import Console

logger = setup_logger('utils', logging.INFO, silent_logging=True)

# Define a more specific exception for retry
RETRY_EXCEPTIONS = (gaierror, ConnectionError)

def retry_on_failure():
    """
    A decorator to retry a function multiple times if it fails with specific exceptions.
    """
    ## grab from our config
    max_retries = config.network_retry_max_retries
    delay = config.network_retry_delay

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RETRY_EXCEPTIONS as e:
                    logger.warning(
                        f"Attempt {attempt + 1} failed with {e}. Retrying in {delay}s..."
                    )
                    if attempt + 1 == max_retries:
                        logger.error(f"All {max_retries} retries failed for {func.__name__}")
                        raise  # Re-raise the last exception
                    time.sleep(delay)

        return wrapper
    return decorator

def is_on_home_network() -> bool:
    """
    Check if the current Wi-Fi SSID is in the list of trusted SSIDs.
    """
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
        logger.info(f"Connected to Wi-Fi: {ssid}")
        assert config.trusted_ssids is not None, "Trusted SSIDs is None"
        return ssid in config.trusted_ssids
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Could not determine Wi-Fi network. Assuming not on a home network.")
        return False

def get_data_download_dir(email_id: int, ensure_exists=True):
    try:
        data_dir = config.paths.get_data_dir()
        download_dir = os.path.join(data_dir, 'downloads')
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)

        ## now lets create the sub dir using the email id
        sub_dir = os.path.join(download_dir, str(email_id))
        logger.debug(f"Download directory: {sub_dir}")
        if ensure_exists:
            os.makedirs(sub_dir, exist_ok=True)
        return sub_dir 
    except Exception as e:
        logger.error(f"Error getting download directory: {e}")
        return None
    
def collect_files_to_print(email_id: int) -> list[str]:
    """ Collects the files to print for an email """
    email_dir = get_data_download_dir(email_id)

    if not os.path.isdir(email_dir):
        logger.info(f"Directory not found for email {email_id}: {email_dir}")
        return []
    
    try:
        all_entries = [os.path.join(email_dir, entry) for entry in os.listdir(email_dir)]
        files = [path for path in all_entries if os.path.isfile(path)]
        ## now sort the files so email.pdf is first and after that the attachments.
        files.sort(key=lambda x: x.endswith('email.pdf'), reverse=True)
        return files
    except OSError as e:
        logger.error(f"Error reading directory {email_dir}: {e}")
        return []

def open_config_dir(console: Console):
    """Opens the application's configuration directory in the file explorer."""
    config_path = config.paths.get_config_dir()
    console.print(f"Opening configuration directory: [bold yellow]{config_path}[/]")
    
    try:
        if sys.platform == "win32":
            subprocess.run(["explorer", str(config_path)], check=True)
        elif sys.platform == "darwin": # macOS
            subprocess.run(["open", str(config_path)], check=True)
        else: # Linux and other Unix-like systems
            subprocess.run(["xdg-open", str(config_path)], check=True)
    except FileNotFoundError:
        console.print("[bold red]Error:[/] Could not open the file explorer.")
        console.print("Please navigate to the directory manually.")
    except Exception as e:
        console.print(f"[bold red]Error:[/] An unexpected error occurred: {e}")


def print_config(console: Console):
    """Prints the configuration."""
    configuration = config.file.get_config()
    for key, value in configuration.items():
        console.print(f"[bold {GREEN}]{key}: {value}[/bold {GREEN}]")
        logger.info(f"{key}: {value}")

def print_dirs(console: Console):
    """Prints the configuration directories."""
    console.print(f"Config directory: {config.paths.get_config_dir()}")
    console.print(f"Data directory: {config.paths.get_data_dir()}")
    console.print(f"Log directory: {config.paths.get_log_dir()}")
    console.print(f"Config file: {config.paths.get_config_filepath()}")
    console.print(f"Secrets file: {config.paths.get_secrets_filepath()}")

def list_cron_jobs(console: Console):
    """Lists the cron jobs."""
    schedule = cron.find_cron_schedule()
    console.print(f"[bold {GREEN}]The cron job is set to {schedule}[/bold {GREEN}]")
    logger.info(f"The cron job is set to {schedule}")
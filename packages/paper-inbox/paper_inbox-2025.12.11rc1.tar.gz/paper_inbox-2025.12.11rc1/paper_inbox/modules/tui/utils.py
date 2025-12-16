import os
import shutil
import subprocess
import time
from functools import wraps
from pathlib import Path
from typing import Callable

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from paper_inbox.modules.config.file import init_config
from paper_inbox.modules.config.paths import (
    get_config_filepath,
    get_refresh_token_filepath,
    get_secrets_filepath,
)
from paper_inbox.modules.const import BEAT, CHECK, CLEAR_SLEEP, CROSS, INDENT, PINK


def clear_previous_lines(lines: int = 1, immediate: bool = False):
    """Moves cursor up N lines and clears them."""
    for _ in range(lines):
        if lines > 1 and not immediate: 
            time.sleep(CLEAR_SLEEP)
        # Moves cursor up one line
        print("\x1b[1A", end="", flush=True)
        # Clears the entire line
        print("\x1b[2K", end="", flush=True)


def show_spinner(message: str, seconds: float = 3.0, indent: bool = True):
    """Shows a spinner for a given duration, updating the message every second."""
    indent_obj = Text("")
    if indent:
        indent_obj = Text(INDENT)
    spinner = Spinner("dots", text=Text.from_markup(message), style=PINK)

    render_table = Table.grid()
    render_table.add_row(indent_obj, spinner)

    with Live(render_table, refresh_per_second=10, transient=True):
        if seconds < 1.0:
            time.sleep(seconds)
        else:
            for i in range(int(seconds)):
                time.sleep(1)
                # Calculate the number of dots to show (1, 2, or 3, then repeat)
                num_dots = (i % 3) + 1
                dots = "." * num_dots
                spinner.text = f"{message}{dots}"


def spinner(message: str, indent: bool = True):
    """Decorator to show a spinner while a function is running."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            indent_obj = Text("")
            if indent:
                indent_obj = Text(INDENT)
            spinner_obj = Spinner("dots", text=Text.from_markup(message), style=PINK)
            render_table = Table.grid()
            render_table.add_row(indent_obj, spinner_obj)

            with Live(render_table, refresh_per_second=10, transient=True):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


def print_text(text: str, console: Console, color: str | None = "blue1", bold: bool = False, indent: bool = False):
    """
    suggested colors are 'blue1' and 'orchid2'
    """
    if color:
        text = f"[{color}]{text}[/]"
        if bold:
            text = f"[bold {color}]{text}[/]"
    else:
        text = f"{text}"
        if bold: 
            text = f"[bold]{text}[/]"

    if indent:
        text = f"{INDENT}{text}"

    console.print(text)

def format_title_success_msgs(msg_A: str, 
                              msg_B: str, 
                              step_number: int | None = None, 
                              total_steps: int | None = None) -> tuple[str, str]:
    """
    Formats the title and success messages for a given step number and total steps.
    Args:
        msg_A: The message for the title.
        msg_B: The message for the success.
        step_number: The current step number.
        total_steps: The total number of steps.
    Returns:
        A tuple containing the formatted title and success messages.
    """
    title_msg = f"{msg_A}"
    success_msg = f"{msg_B}"
    if step_number is not None and total_steps is not None:
        title_msg = f"[{step_number} / {total_steps}] {msg_A}"
        success_msg = f"{step_number}. {CHECK} {msg_B}"

    return title_msg, success_msg

def format_failure_msg(failure_msg: str, step_number: int | None = None, total_steps: int | None = None) -> str:
    """
    Formats the failure message for a given step number and total steps.
    Args:
        failure_msg: The failure message.
        step_number: The current step number.
        total_steps: The total number of steps.
    Returns:
        The formatted failure message.
    """
    if step_number is not None and total_steps is not None:
        failure_msg = f"{step_number}. {CROSS} {failure_msg}"
    return failure_msg

## this is deprecated and we should remove it when we can..
def get_line(text: str, color: str = "blue1", bold: bool = True, newline_suffix: bool = False, newline_prefix: bool = False):
    if newline_suffix:
        text = f"{text}\n"
    if newline_prefix:
        text = f"\n{text}"
    
    if color:
        text = f"[{color}]{text}[/]"
        if bold:
            text = f"[bold {color}]{text}[/]"
    else:
        text = f"{text}"
        if bold: 
            text = f"[bold]{text}[/]"

    return Text.from_markup(text)

@spinner("Checking for existing config file...")
def does_config_exist():
    time.sleep(BEAT * 2)
    config_path = get_config_filepath()
    if not config_path.exists():
        return False
    return True

@spinner("Creating config file...")
def create_config_file():
    time.sleep(BEAT * 2)
    init_config() 
    return True

@spinner("Checking for SSID...")
def get_SSID():
    time.sleep(BEAT)
    res = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
    return res

@spinner("Checking gmail authentication...")
def does_secrets_file_exist(ux_delay: bool = False):
    if ux_delay:
        time.sleep(4)
    filepath = get_secrets_filepath()
    if not os.path.exists(filepath):
        return False
    if not os.path.isfile(filepath):
        return False
    return True

@spinner("Copying client_secrets.json file...")
def copy_secrets_file(filepath: str):
    time.sleep(BEAT)
    # Convert the string path into a Path object
    source_path = Path(filepath)
    destination_path = get_secrets_filepath()

    # Copy the file
    shutil.copy(source_path, destination_path)
    return True

@spinner("Checking for refresh_token.json file...")
def does_refresh_token_file_exist(ux_delay: bool = False):
    if ux_delay:
        time.sleep(BEAT)
    filepath = get_refresh_token_filepath()
    if not os.path.exists(filepath):
        return False
    if not os.path.isfile(filepath):
        return False
    return True
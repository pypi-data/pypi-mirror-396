import logging
import subprocess
import time

import click
from rich.console import Console

from paper_inbox.main import run_app
from paper_inbox.modules.const import GREEN, RED, SEPARATOR
from paper_inbox.modules.loggers import setup_logger
from paper_inbox.modules.tui import render, user
from paper_inbox.modules.tui.utils import clear_previous_lines, print_text
from paper_inbox.modules.utils import (
    list_cron_jobs,
    open_config_dir,
    print_config,
    print_dirs,
)

console = Console()

logger = setup_logger('cli', logging.INFO, silent_logging=True)

@click.group(invoke_without_command=True)
@click.option('--config', is_flag=True, help='Configure the application.')
@click.option('--show-config', is_flag=True, help='Show the configuration.')
@click.option('--show-dirs', is_flag=True, help='Show the configuration directories.')
@click.option('--show-cron', is_flag=True, help='List the cron schedule.')
@click.option('--open-config', is_flag=True, help='Open the configuration directory.')
@click.option('--test', is_flag=True, help='Run tests.')
@click.pass_context
def main(ctx, config, show_config, show_dirs, show_cron, open_config, test):
    """"""
    if ctx.invoked_subcommand is None:
        ## check if all passed command flags were False
        all_cmds = [config, show_config, show_dirs, show_cron, open_config, test]
        if all(not cmd for cmd in all_cmds):
            run_app()
            return
        
        if config:
            configure_app()
        elif show_config:
            print_config(console)
        elif show_dirs:
            print_dirs(console)
        elif show_cron:
            list_cron_jobs(console)
        elif open_config:
            open_config_dir(console)
        elif test:
            run_tests()
        else:
            console.print("[bold red]Error:[/] No valid command flags passed. Please use --config, --show-config, --show-dirs, or --show-cron.")

def run_tests():
    """Runs the tests."""
    console.print(f"[bold {GREEN}]Running tests...[/bold {GREEN}]")
    logger.info("Running tests...")
    ## run the tests
    results = subprocess.run(["pytest", "tests"], check=False)
    if results.returncode == 0:
        console.print(f"[bold {GREEN}]Tests completed successfully.[/bold {GREEN}]")
        logger.info("Tests completed successfully.")
    else:
        console.print(f"[bold {RED}]Tests failed.[/bold {RED}]")
        logger.error("Tests failed.")

def configure_app():
    step_count = 5
    console.clear()
    ## run the steps and store the resultsA
    failed_items = []
    failed_items.extend(render.dependency_validation(console, 1, step_count))
    failed_items.extend(render.config_setup(console, 2, step_count))
    failed_items.extend(render.network_setup(console, 3, step_count))
    failed_items.extend(render.cron_setup(console, 4, step_count))
    failed_items.extend(render.auth_setup(console, 5, step_count))


    # optional steps we wrap in a confirmation step
    confirm = user.confirm('Set up Telegram notifications? (optional)', indent=False)
                           
    if confirm:
        failed_items.extend(render.telegram_bot_setup(console, 6, step_count))
        step_count += 1

    time.sleep(2)
    if not failed_items:
        clear_previous_lines(step_count) ## clear out all the lines to just show success
        print_text("Initialization complete", console, GREEN, bold=True)
    else:
        failure_count = len(failed_items)
        print_text(SEPARATOR, console, None, bold=True)
        print_text(f"Initialization failed: {failure_count} steps failed", console, "red", bold=True)
        print_text(SEPARATOR, console, None, bold=True)
        for item in failed_items:
            print_text(f" - {item.name}: {item.get_msg()}", console, "red", bold=True)
            print_text(item.feedback, console, None, bold=True)



if __name__ == "__main__":
    main()

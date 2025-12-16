import logging
import time
from functools import wraps

from rich.console import Console

from paper_inbox.modules import config, cron, dependencies, tui
from paper_inbox.modules.auth import gmail
from paper_inbox.modules.const import BEAT, BLUE, CHECK, GREEN, INDENT_Q_NEWLINE, RED
from paper_inbox.modules.loggers import setup_logger
from paper_inbox.modules.tui import user
from paper_inbox.modules.tui.info import SubStepFeedback

logger = setup_logger('tui_render', logging.INFO, silent_logging=True)


def setup_step(msg_A: str, msg_B: str, lines_to_clear: int = 2):
    """
    Decorator that handles the common setup/teardown pattern for setup steps.
    
    Args:
        msg_A: The title message (e.g., "Setting up the network")
        msg_B: The success message (e.g., "Network setup complete")
        lines_to_clear: Base number of lines to clear at the end (can be modified by function)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(console: Console, 
                    step_number: int | None = None, 
                    total_steps: int | None = None):
            ## format the title and success messages
            failure_msg = None
            title_msg, success_msg = tui.utils.format_title_success_msgs(msg_A, 
                                                               msg_B, 
                                                               step_number, 
                                                               total_steps)
            ## print the main title message for this step
            tui.utils.print_text(title_msg, console, BLUE, bold=True)
            
            # EXECUTION PHASE - call the actual function
            # The function can return:
            # - None (success with default line clearing)
            # - (failure_msg, extra_lines) tuple
            # - failure_msg string only
            result = func(console)
            
            # Handle different return types
            failure_items = []
            extra_lines = 0
            if isinstance(result, tuple):
                failure_items, extra_lines = result
            elif isinstance(result, list):
                failure_items = result
            elif result is not None:
                failure_items = result
            
            # TEARDOWN PHASE
            time.sleep(1)
            tui.utils.clear_previous_lines(lines_to_clear + extra_lines)

            if failure_items:
                for item in failure_items: 
                    msg = tui.utils.format_failure_msg(item.get_msg(), step_number, total_steps)
                    tui.utils.print_text(msg, console, RED, bold=True)
                return failure_items
            
            tui.utils.print_text(success_msg, console, GREEN, bold=True)
            return [] ## return empty list, no failures
        
        return wrapper
    return decorator

@setup_step("Checking for system dependencies", "System dependencies found", lines_to_clear=4)
def dependency_validation(console: Console, 
                          step_number: int | None = None, 
                          total_steps: int | None = None):
    """
    Validates the system dependencies by showing a spinner and running a function.
    Args:
        console: The console to use.
        step_number: The current step number.
        total_steps: The total number of steps.
    """
    failed_items = []

    ## -- cups ---
    if not dependencies.is_cups_installed():
        item = SubStepFeedback("CUPS", failed=True)
        item.print(console)
        failed_items.append(item)
    else:
        item = SubStepFeedback("CUPS", failed=False)
        item.print(console)

    ## -- libreoffice ---
    if not dependencies.is_libreoffice_installed():
        item = SubStepFeedback("libreoffice", failed=True)
        item.print(console)
        failed_items.append(item)
    else:
        item = SubStepFeedback("libreoffice", failed=False)
        item.print(console)

    return failed_items

@setup_step("Setting up the configuration", "Configuration complete", lines_to_clear=4)
def config_setup(console: Console, 
                 step_number: int | None = None, 
                 total_steps: int | None = None):
    """
    Sets up the configuration by showing a spinner and running a function.
    Args:
        console: The console to use.
        step_number: The current step number.
        total_steps: The total number of steps.
    """
    failed_items = []

    ## --- config file ---
    config_exists = tui.utils.does_config_exist()
    if not config_exists:
        res = tui.utils.create_config_file()
        tui.utils.print_text(f"{CHECK} Config file created", console, None, indent=True)
    else:
        tui.utils.print_text(f"{CHECK} Config file found", console, None, indent=True)


    ## --- email inbox ---
    tui.utils.show_spinner("Let's set up your email address", BEAT)
    has_account = config.validators.has_email_account_defined()
    if not has_account:
        email_inbox = user.get_email_address("What is your email address?", 
                                             example="your_email@example.com")
        if email_inbox:
            config.setters.set_email_account(email_inbox)
            item = SubStepFeedback("inbox_email", add_info=email_inbox)
            item.print(console)
        else:
            item = SubStepFeedback("inbox_email", failed=True)
            item.print(console)
            failed_items.append(item)
    else:
        item = SubStepFeedback("inbox_email.already_setup", failed=False)
        item.print(console)

    ## --- sender emails --- 
    tui.utils.show_spinner("Let's set up the sender emails", BEAT)
    has_senders = config.validators.has_sender_emails_defined()
    extra_count = 0 
    if not has_senders:
        from_emails = []
        sender_email = user.get_email_address("What's the sender email address?", example="sender@example.com")
        ask_for_more = True
        ## keep track of the amount of extra times we add email, 
        ## so we can clear correct number of lines.
        while ask_for_more:
            if sender_email:
                config.setters.add_from_email(sender_email)
                item = SubStepFeedback("sender_emails", add_info=sender_email)
                item.print(console)
                time.sleep(BEAT)
                ask_for_more = user.confirm('Would you like to add another sender email?')
                if ask_for_more:
                    extra_count += 1
                    sender_email = user.get_email_address("What's another senders email address?")
                else:
                    ask_for_more = False
            else:
                item = SubStepFeedback("sender_emails", failed=True)
                item.print(console)
                failed_items.append(item)
                ask_for_more = False
    else:
        item = SubStepFeedback("sender_emails.already_setup")
        item.print(console)

    return failed_items, extra_count

@setup_step("Setting up the network", "Network setup complete", lines_to_clear=2)
def network_setup(console: Console, 
                  step_number: int | None = None, 
                  total_steps: int | None = None):
    """
    Sets up the network by showing a spinner and running a function.
    Args:
        console: The console to use.
        step_number: The current step number.
        total_steps: The total number of steps.
    """
    failed_items = []

    ## now go through the sub steps
    has_network = config.validators.has_trusted_network_defined()
    if not has_network:
        ## --- network ---
        ssid = tui.utils.get_SSID()
        if not ssid:
            item = SubStepFeedback("network", failed=True)
            item.print(console)
            failed_items.append(item)
            return failed_items ## return right away
        
        ## -- add it as a trusted network ---
        msg = f"Found WIFI network: {ssid}.{INDENT_Q_NEWLINE}Shall I add it to the trusted networks?"
        add_ssid = user.confirm(msg, indent=True, line_count=2)
        if add_ssid: 
            config.setters.add_trusted_network(ssid)
            item = SubStepFeedback("network", add_info=ssid)
            item.print(console)
        else:
            item = SubStepFeedback("network.not_added", failed=True)
            item.print(console)
            failed_items.append(item)
    else:
        item = SubStepFeedback("network.already_setup", failed=False)
        item.print(console)
    
    return failed_items

@setup_step("Setting up the cron", "Cron setup complete", lines_to_clear=1)
def cron_setup(console: Console, 
               step_number: int | None = None, 
               total_steps: int | None = None):
    """
    Sets up the cron by showing a spinner and running a function.
    Args:
        console: The console to use.
        step_number: The current step number.
        total_steps: The total number of steps.
    """
    failed_items = []
    extra_lines= 0
    
    ## now go through the sub steps
    ## --- cron schedule ---
    current_cron_schedule = cron.find_cron_schedule()
    msg = "Would you like to set up a cron job?" ## init 
    lines_to_clear = 1
    if current_cron_schedule:
        tui.utils.print_text(f"Currently the cron job is set to {current_cron_schedule}", console, None, indent=True)
        msg = "Would you like to change it?"
        lines_to_clear = 2
    confirm = user.confirm(msg, indent=True, line_count=lines_to_clear)

    new_cron_schedule = None
    if not confirm and current_cron_schedule:
        item = SubStepFeedback("cron.continue_existing") ## success
        item.print(console)
        extra_lines += 1
        return [], extra_lines ## return empty list, no failures
    elif not confirm and not current_cron_schedule:
        item = SubStepFeedback("cron.not_set", failed=True)
        item.print(console)
        failed_items.append(item)
        extra_lines += 1
        return failed_items, extra_lines
        
    new_cron_schedule = user.choose_cron_schedule("What's the new cron schedule?")
    if new_cron_schedule: ## if there's a new cron schedule selected, lets set it up
        cron.set_cron_schedule(new_cron_schedule)
    else:
        cron.remove_cron_schedule()
        item = SubStepFeedback("cron.removed", failed=True)
        item.print(console)
        failed_items.append(item)
        extra_lines += 1

    return failed_items, extra_lines


@setup_step("Setting up Gmail authentication", "Gmail authentication complete", lines_to_clear=2)
def auth_setup(console: Console, 
                  step_number: int | None = None, 
                  total_steps: int | None = None):
    """
    Sets up the authentication secrets by showing a spinner and running a function.
    Args:
        console: The console to use.
        step_number: The current step number.
        total_steps: The total number of steps.
    """
    failed_items = []
    extra_lines = 0

    ## now go through the sub steps
    existing = tui.utils.does_secrets_file_exist(ux_delay=True)
    filepath = None 
    if not existing:
        filepath = user.get_secrets_from_command_line()
        if filepath is None and existing:
            item = SubStepFeedback("client_secrets.continue_existing")
            item.print(console)
        elif filepath is None and not existing: ## no new file and no existing file
            item = SubStepFeedback("client_secrets.not_provided", failed=True)
            item.print(console)
            failed_items.append(item)
            # extra_lines += 1
    else:
        item = SubStepFeedback("client_secrets.already_setup")
        item.print(console)

    
    if filepath is not None:
        logger.info(f"New client_secrets.json file provided: {filepath}, {type(filepath)}")
        item = SubStepFeedback("client_secrets.new_file")
        copied = tui.utils.copy_secrets_file(filepath)
        if copied:
            item = SubStepFeedback("client_secrets")
            item.print(console)
        else:
            logger.error(f"Could not copy the client_secrets file: {filepath}")
            item = SubStepFeedback("client_secrets", add_info=filepath, failed=True)
            item.print(console)
            failed_items.append(item)
            # extra_lines += 1
            ## maybe return right away...

    refresh_exists= tui.utils.does_refresh_token_file_exist(ux_delay=True)
    if not refresh_exists:
        ## check if the client_secrets file does exist
        if not tui.utils.does_secrets_file_exist(ux_delay=True):
            item = SubStepFeedback("refresh_token.no_secrets_file", failed=True)
            item.print(console)
            failed_items.append(item)
            # extra_lines += 1
            return failed_items, extra_lines ## return right away
        else:
            ## set up the refresh token
            gmail.set_refresh_token()
            item = SubStepFeedback("refresh_token")
            item.print(console)
            extra_lines += 1

    return failed_items, extra_lines

@setup_step("Setting up Telegram notifications", "Telegram bot setup complete", lines_to_clear=3)
def telegram_bot_setup(console: Console, 
                       step_number: int | None = None, 
                       total_steps: int | None = None):
    """
    Sets up the Telegram bot by showing a spinner and running a function.
    Args:
        console: The console to use.
        step_number: The current step number.
        total_steps: The total number of steps.
    """
    failed_items = []

    ## now go through the sub steps
    ## --- get the bot token ---
    bot_token = user.get_telegram_bot_token()
    if bot_token:
        config.setters.set_telegram_bot_token(bot_token)
        item = SubStepFeedback("telegram.token", add_info=bot_token)
        item.print(console)
    else:
        item = SubStepFeedback("telegram.token", failed=True)
        item.print(console)
        failed_items.append(item)

    ## --- get the chat id ---
    chat_id = user.get_telegram_chat_id()
    if chat_id:
        config.setters.set_telegram_chat_id(chat_id)
        item = SubStepFeedback("telegram.chat_id", add_info=chat_id)
        item.print(console)
    else:
        item = SubStepFeedback("telegram.chat_id", failed=True)
        item.print(console)
        failed_items.append(item)

    if len(failed_items) == 0:
        config.setters.set_send_telegram_notifications(True) ## switch it on

    return failed_items
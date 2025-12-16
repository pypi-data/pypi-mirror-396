import questionary
from platformdirs import user_downloads_dir

from paper_inbox.modules.const import INDENT, INDENT_Q_NEWLINE, QMARK_PREFIX
from paper_inbox.modules.tui import validators
from paper_inbox.modules.tui.utils import clear_previous_lines


def confirm(msg: str = "Do you want to proceed?", 
            choices: list = ["Yes", "No"], 
            indent: bool = False, 
            line_count: int = 1):
    """Asks for a TUI-style confirmation and exits."""
    qmark = QMARK_PREFIX if indent else '?'
    proceed = questionary.select(msg, 
                                 choices=choices, 
                                 qmark=qmark).ask()
    clear_previous_lines(line_count)

    if proceed == "No":
        return False

    if proceed:
        return True
    else:
        return False

def choose_cron_schedule(msg: str = "What's the cron schedule?"):
    choices = [
        "Every 1 hour",
        "Every 4 hours",
        "Every hour during 8 AM - 6 PM",
        "Custom schedule",
        "Never"
    ]
    choice = questionary.select(msg, choices=choices).ask()
    clear_previous_lines(1)

    ## let's get the index of the choice.
    index = choices.index(choice)
    if index == 0: ## every 1 hours
        return "0 * * * *"
    elif index == 1: ## every 4 hours
        return "0 */4 * * *"
    elif index == 2: ## every hour during 8 AM - 6 PM
        return "0 8-18 * * *"
    elif index == 4: ## the never case
        return None
    elif index == 3: ## custom schedule
        custom_schedule = questionary.text("Provide the cron schedule:", qmark=QMARK_PREFIX).ask()
        clear_previous_lines(1)
        return custom_schedule 

def get_email_address(msg: str = "What's your email address?", example: str | None = None):
    success = False
    count = 0
    org_msg = str(msg)
    while not success:
        if count == 0:
            msg = f"{org_msg}"
        else:
            msg = f"Invalid address: {org_msg}"


        ## depending if we provide an example, 
        ## we change the message and the instructions a little
        prefix = QMARK_PREFIX
        instruction = None
        msg_to_show = f"{msg} > "
        line_count = 1
        if example:
            instruction = f'\n{INDENT}e.g. {example} >'
            msg_to_show = f"{msg}"
            line_count = 2
        email = questionary.text(msg_to_show, 
                                 qmark=prefix,
                                 instruction=instruction,
                                 multiline=False).ask()
        clear_previous_lines(line_count, immediate=True)
        success = validators.is_valid_email_address(email)
        count += 1
        if count >= 3:
            return None

    ## generally we need to clear the 1 previous line
    return email

def confirm_secrets_strategy():
    choices = [
        "write path to file on command line",
        "open file explorer, paste file in there",
    ]
    choice = questionary.select(
        "How would you like to set the client_secret.json?", 
        choices=choices).ask()
    clear_previous_lines(1)

    if choices.index(choice) == 0:
        return 1
    if choices.index(choice) == 1:
        return 2
    return None

def get_secrets_from_command_line():
    default_dir = user_downloads_dir()

    success = False
    count = 0
    while not success and count < 3:
        msg = "provide the path to your client secrets file."
        msg += INDENT_Q_NEWLINE
        msg += "you receive this file after setting up your app in your Google Cloud Console"
        msg += INDENT_Q_NEWLINE
        msg += "> "
        if count == 0:
            msg = f"{msg}"
        else:
            msg = f"Invalid path: {msg}"

        path = questionary.path(msg,
                                qmark=QMARK_PREFIX,
                                default=default_dir).ask()
        clear_previous_lines(3, immediate=True)
        success = validators.is_valid_client_secrets_path(path)

        count += 1
    ## again run the validation to make sure the path is valid
    if not validators.is_valid_client_secrets_path(path):
        return None
    return path

def get_secrets_from_explorer():
    return True

def get_telegram_bot_token():
    bot_token = questionary.text("What's your Telegram bot token?",
                                 qmark=QMARK_PREFIX).ask()
    clear_previous_lines(1)
    return bot_token

def get_telegram_chat_id():
    chat_id = questionary.text("What's your Telegram chat id?",
                               qmark=QMARK_PREFIX).ask()
    clear_previous_lines(1)
    return chat_id
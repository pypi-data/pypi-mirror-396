from typing import Union

from rich.console import Console

from paper_inbox.modules.const import CHECK, CROSS, INFO_INDENT, SEPARATOR
from paper_inbox.modules.tui.utils import print_text


class SubStepFeedback:
    def __init__(self, 
                 step_name: str, 
                 failed: bool = False, 
                 type: str | None = None,
                 add_info: str | None = None):
        self.step_name = step_name
        self.failed = failed
        self.type = type
        self.add_info = add_info or 'placeholder'
        self.setup()

    def setup(self):
        if self.step_name.lower() == "cups":
            self.name = 'CUPS'
            self.success = "CUPS installed"
            self.fail = "cups is not installed"
            self.feedback = install_info_cups()
        
        elif self.step_name.startswith("libreoffice"):
            self.name = 'LibreOffice'
            self.success = "LibreOffice installed"
            self.fail = "LibreOffice is not installed"
            self.feedback = install_info_libreoffice()
        
        elif self.step_name.startswith("inbox_email"):
            self.name = 'Email inbox'
            self.success = f"Email inbox added: {self.add_info}"
            self.fail = "No email inbox added"
            self.feedback = email_inbox_fail()
            if self.step_name.endswith(".already_setup"):
                self.success = "Email inbox already set up"
        
        elif self.step_name.startswith("sender_emails"):
            self.name = "Sender emails"
            self.success = f"Sender emails added: {self.add_info}"
            self.fail = "No sender emails added"
            self.feedback = email_sender_fail()
            if self.step_name.endswith(".already_setup"):
                self.success = "Sender emails already set up"
        
        elif self.step_name.startswith("client_secrets"):
            self.name = 'Authentication'
            self.success = "Set up the authentication with Gmail"
            self.fail = "Could not copy the client_secrets file"
            self.feedback = client_secrets_fail()

            if self.step_name.endswith(".already_setup"):
                self.success = "Authentication already set up"

            if self.step_name.endswith('.new_file'):
                self.success = "New client_secrets.json file provided"

            if self.step_name.endswith(".not_provided"):
                self.fail = "No client_secrets.json file provided"
                self.feedback = format_feedback_lines("Provide a valid client secrets json file")

            if self.step_name.endswith('.continue_existing'):
                self.success = "No new secrets file provided, continuing to use existing one"

        elif self.step_name.startswith("refresh_token"):
            self.name = "Authentication"
            self.success = "Set up refresh token"
            self.fail = "Could not set up refresh token"
            self.feedback = format_feedback_lines("No refresh token file provided")

            if self.step_name.endswith(".no_secrets_file"):
                self.fail = "No authentication set up"
                self.feedback = format_feedback_lines("Without initial authentication, no refresh token can be set up")
        
        elif self.step_name.startswith("network"):
            self.name = "Network wifi"
            self.success = f"Added a wifi as trusted network: {self.add_info}"
            self.fail = "Could not detect wifi network"
            self.feedback = format_feedback_lines("Connect to a wifi network")

            if self.step_name.endswith(".not_added"):
                self.fail = "Wifi not added as trusted network"
                self.feedback = format_feedback_lines("Add the wifi network to the trusted networks")

            if self.step_name.endswith(".already_setup"):
                self.success = "Trusted wifi network already set up"

        elif self.step_name.startswith("cron"):
            self.name = "Cron"
            self.success = f"Cron job set to {self.add_info}"
            self.fail = "Could not set up cron job"
            self.feedback = format_feedback_lines("Enter a valid cron schedule")

            if self.step_name.endswith(".continue_existing"):
                self.success = "Will continue using existing cron schedule"

            if self.step_name.endswith(".not_set"):
                self.fail = "No cron schedule provided"
                self.feedback = format_feedback_lines("Enter a valid cron schedule")
            
            if self.step_name.endswith(".removed"):
                self.fail = "Cron job removed, will not run automatically"
                self.feedback = format_feedback_lines("To monitor your inbox, set up a new cron job")

        elif self.step_name.startswith("telegram"):
            self.name = "Telegram"
            self.success = "Set up Telegram notifications"
            self.fail = "Could not set up Telegram notifications"
            self.feedback = format_feedback_lines("Enter a valid Telegram bot token and chat id")

            if self.step_name.endswith(".token"):
                self.success = f"Telegram bot token added: {self.add_info}"
                self.fail = "No telegram bot token provided"
                self.feedback = format_feedback_lines("Enter a valid Telegram bot token")

            if self.step_name.endswith(".chat_id"):
                self.success = f"Telegram chat id added: {self.add_info}"
                self.fail = "No telegram chat id provided"
                self.feedback = format_feedback_lines("Enter a valid Telegram chat id")
        else:
            self.name = 'Unknown'
            self.success = 'Unknown step'
            self.fail = 'Unknown step'
            self.feedback = 'Unknown feedback'

    def get_msg(self):
        if not self.failed:
            return self.success
        else:
            return self.fail

    def print(self, console: Console):
        """
        Prints the feedback to the console.
        Args:
            console: The console to use.
        """
        if not self.failed:
            print_text(f"{CHECK} {self.success}", console, None, indent=True)
        else:
            print_text(f"{CROSS} {self.fail}", console, None, indent=True)


def format_feedback_lines(feedback: Union[list[str], str]) -> str:
    if isinstance(feedback, str):
        feedback = [feedback]

    msg = ""
    for line in feedback:
        msg += f"{INFO_INDENT}{line}\n"
    return msg

def install_info_cups() -> str:
    lines = ["Install CUPS by running: ",
             SEPARATOR,
             "sudo apt update",
             "sudo apt install -y cups",
             SEPARATOR]
    msg = format_feedback_lines(lines)
    return msg

def install_info_wkhtmltopdf() -> str:
    lines = ["Install wkhtmltopdf by running: ",
             SEPARATOR,
             "sudo apt update",
             "sudo apt install -y wkhtmltopdf",
             SEPARATOR]
    msg = format_feedback_lines(lines)
    return msg

def install_info_libreoffice() -> str:
    lines = ["Install LibreOffice by running: ",
             SEPARATOR,
             "sudo apt update"
             "sudo apt install -y libreoffice",
             SEPARATOR]
    msg = format_feedback_lines(lines)
    return msg

def client_secrets_fail() -> str:
    lines = ["Could not copy the client_secrets file, copy the client_secrets.json",
             "file manually to the correct location and try again"]
    msg = format_feedback_lines(lines)
    return msg

def email_inbox_fail() -> str:
    lines = ["No email account provided to read the inbox from",
             "Enter a valid email address"]
    msg = format_feedback_lines(lines)
    return msg

def email_sender_fail() -> str:
    lines = ["No sender email address provided, to trigger the prints"]
    msg = format_feedback_lines(lines)
    return msg
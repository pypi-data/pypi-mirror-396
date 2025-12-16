import logging
import sys
import time

from paper_inbox.modules import config, tui
from paper_inbox.modules.database.utils import (
    does_database_exist,
    get_database_handle,
    get_email_from_db_by_id,
    get_unprinted_emails,
    set_all_emails_as_printed,
    set_email_as_printed,
    update_email_attachments,
)
from paper_inbox.modules.email import (
    add_email_to_database,
    distill_new_emails_from_latest,
    download_attachments,
    download_email,
    fetch_latest_emails,
    get_fullpaths_for_attachments,
)
from paper_inbox.modules.loggers import setup_logger
from paper_inbox.modules.pdf import utils as pdf
from paper_inbox.modules.printer.utils import print_file
from paper_inbox.modules.telegram import send_telegram_notification
from paper_inbox.modules.utils import collect_files_to_print, retry_on_failure

logger = setup_logger('main', logging.INFO, False)

@retry_on_failure()
def run_app():
    """
    Main function to check for new emails and print them.
    """
    validate_dependencies()
    validate_config()
    validate_auth()

    is_initial_run = False if does_database_exist() else True 
    db = get_database_handle(delete_existing=False)
    logger.info(f"Is this an initial run? {is_initial_run}")

    ## now check the emails
    fetch_count, new_count = check_emails(initial_run=is_initial_run)
    ## and print them
    print_count = print_emails()
    ## send a message to telegram if it's turned on.
    msg = f"Checked {fetch_count} emails, found {new_count} new emails, printed {print_count} emails"
    send_telegram_notification(msg)
    logger.info(msg)

def validate_dependencies():
    """Checks for required system dependencies and exits if they are not found."""
    if not config.cups_path:
        logger.error("CUPS not found. Please install it and ensure it's in your PATH, or set the LPSTAT_PATH environment variable.")
        sys.exit(1)
    if not config.libreoffice_path:
        logger.error("LibreOffice is not installed or not in PATH. Printing .docx files will fail.")
        sys.exit(1)

def validate_config():
    if not config.email_account:
        logger.error("No email account found. Please set up your email account in the --config command.")
        sys.exit(1)
    if not config.email_senders:
        logger.error("No email senders found. That means no emails will be monitored. Please set up your email senders in the --config command.")
        sys.exit(1)
    if not config.trusted_ssids:
        logger.error("No trusted SSIDs found. Please set up your trusted SSIDs in the --config command.")
        sys.exit(1)

def validate_auth():
    if not tui.utils.does_refresh_token_file_exist():
        logger.error("No refresh token found. Please set up your refresh token in the --config command.")
        sys.exit(1)
    if not tui.utils.does_secrets_file_exist():
        logger.error("No client secrets found. Please set up your client secrets in the --config command.")
        sys.exit(1)


def check_emails(initial_run: bool = False):
    """ 
    checks for new emails, 
    downloads them and their attachments, 
    then adds them to the database
    --
    If initial_run is True, it will set all emails as printed, 
    to avoid printing out old emails when running the script for the first time.
    """
    db = get_database_handle(delete_existing=False)
    latest = fetch_latest_emails(only_unseen=True, 
                                 mark_as_read=False, 
                                 days_limit=10, 
                                 limit=20)
    fetched_subjects = [email.get('subject') for email in latest]
    logger.info(f'the latest fetched emails are these: {fetched_subjects}')
    ## now parse the emails to find out which ones are actually new.
    new = distill_new_emails_from_latest(latest) or []
    if not new:
        logger.info("No new emails found")
        return len(latest), len(new)
    
    logger.info(f"Found {len(new)} new emails")
    ## lets download the emails and the attachments
    for email in new:
        email_id = add_email_to_database(email, db)
        attachments = download_attachments(email, email_id)
        ## get the full paths for the attachments, and validate them
        fullpaths = get_fullpaths_for_attachments(attachments, email_id)
        pdf.validate_pdfs(fullpaths)
        ## update the database
        update_email_attachments(email_id, attachments)
        ## finally generate / download the email as a html file.
        html_filepath = download_email(email_id)

    if initial_run:
        set_all_emails_as_printed()
        logger.info("Set all emails as printed for initial run")

    ## lets return the count for the fetched and new emails.
    return len(latest), len(new)

def print_emails(limit: int = 3) -> int:
    """ 
    checks for unprinted emails,
    prints them, makes sure they are completed,
    then sets them as printed in the database
    returns count of emails printed
    """
    unprinted_emails = get_unprinted_emails()
    logger.info(f"Found {len(unprinted_emails)} unprinted emails in the database")

    ## keep count of the emails printed
    emails_printed = 0
    for email in unprinted_emails[:limit]:
        email_id = email.get('id')
        assert email_id is not None, "Email ID is None"

        email_obj = get_email_from_db_by_id(email_id)
        email_subject = email_obj.get('subject')
        files_to_print = collect_files_to_print(email_id)

        completed_list = []
        for filepath in files_to_print:
            logger.info(f"Printing file: {filepath}")
            if not pdf.is_valid(filepath): ## guard printer against invalid pdfs
                continue
            completed = print_file(filepath)
            completed_list.append(completed)
            time.sleep(1)

        if not all(completed_list):
            logger.error(f"Failed to print some files for email {email_id}")
            time.sleep(3)
            continue

        logger.info(f"All files printed successfully for email {email_id}")
        set_email_as_printed(email_id)

        ## message to send to telegram
        msg = f"New email with subject: '{email_subject}' has been printed just now..."
        send_telegram_notification(msg)
        logger.info(msg)
        emails_printed += 1
        time.sleep(3)

    return emails_printed

if __name__ == "__main__":
    run_app()

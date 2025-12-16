import logging
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from paper_inbox.modules.config.paths import (
    get_refresh_token_filepath,
    get_secrets_filepath,
)
from paper_inbox.modules.loggers import setup_logger
from paper_inbox.modules.utils import retry_on_failure

logger = setup_logger('gmail', logging.INFO, silent_logging=True)

# Use the full-access scope that the IMAP server is demanding
SCOPES = ['https://mail.google.com/']
TOKEN_PATH = str(get_refresh_token_filepath())
CLIENT_SECRETS_PATH = str(get_secrets_filepath())

@retry_on_failure()
def get_credentials() -> Credentials | None:
    """
    Loads and refreshes Google OAuth 2.0 credentials from token.json.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the refreshed credentials back to the file
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        else:
            # This should not happen in a cron job.
            # The token.json should be created beforehand by running the authorize script.
            raise FileNotFoundError(
                f"'{TOKEN_PATH}' not found. "
                "Please run the config setup first to generate it."
            )
            
    return creds

def set_refresh_token():
    """
    Runs the OAuth 2.0 flow to get credentials and saves them to token.json.
    If token.json already exists, it will refresh the token if necessary.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            logger.info("No valid credentials found, starting authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_PATH, SCOPES)
            
            ## suppress the stdout output from run_local_server
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                creds = flow.run_local_server(port=0)
            finally:
                sys.stdout = old_stdout

        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            logger.info(f"Credentials saved to {TOKEN_PATH}")





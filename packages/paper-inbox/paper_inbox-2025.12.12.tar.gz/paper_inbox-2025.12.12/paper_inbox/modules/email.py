from __future__ import annotations

import email
import imaplib
import logging
import os
from datetime import datetime, timedelta
from email.message import Message
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import TYPE_CHECKING, List

from paper_inbox.modules import config
from paper_inbox.modules.auth.gmail import get_credentials
from paper_inbox.modules.config.paths import get_refresh_token_filepath
from paper_inbox.modules.database.utils import does_email_exist, get_email_from_db_by_id
from paper_inbox.modules.loggers import setup_logger
from paper_inbox.modules.pdf import utils as pdf
from paper_inbox.modules.printer import convert
from paper_inbox.modules.printer.generate import generate_email_pdf
from paper_inbox.modules.utils import get_data_download_dir, retry_on_failure

if TYPE_CHECKING:
    from paper_inbox.modules.database.sqlwrapper import SQLiteWrapper

logger = setup_logger('email', logging.INFO, False)

SCOPES = ['https://mail.google.com/']
TOKEN_PATH = str(get_refresh_token_filepath())


def download_attachments(msg: Message, email_id: int) -> list[str]:
    """
    Downloads attachments from an email.
    """
    attachments = []
    email_dir = get_data_download_dir(email_id)
    accepted_content_types = ["application/pdf", 
                              "application/msword", 
                              "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] ## .docx
    
    for part in msg.walk():
        if part.get_content_type() in accepted_content_types:
            filename = part.get_filename()
            if not filename:
                continue
            ## only create the dir once we know we have
            ## a pdf to store there..
            os.makedirs(email_dir, exist_ok=True)
            filepath = os.path.join(email_dir, filename)
            with open(filepath, "wb") as f:
                payload = part.get_payload(decode=True)
                assert isinstance(payload, bytes), "Email part payload must be bytes"
                f.write(payload)
            
            if filename.lower().endswith(".docx"):
                pdf_filepath = convert.docx_to_pdf(filepath)
                if pdf_filepath:
                    os.remove(filepath) # Delete the original .docx file
                    # Use the new PDF filename
                    filename = os.path.basename(pdf_filepath)
            attachments.append(filename)

    return attachments

def get_fullpaths_for_attachments(filenames: list[str], email_id: int) -> list[Path]:
    email_dir = get_data_download_dir(email_id)
    full_paths = [(Path(email_dir) / x) for x in filenames]
    return full_paths

def download_email(email_id: int) -> str:
    """
    email_id: the id of the email in the database.
    Returns the path to the HTML and text files.
    """
    email_obj = get_email_from_db_by_id(email_id)
    email_dir = get_data_download_dir(email_id, ensure_exists=True)
    email_filepath = generate_email_pdf(email_obj, email_dir)
    assert email_filepath is not None, "Email filepath is None"

    return email_filepath 

@retry_on_failure()
def fetch_latest_emails(only_unseen: bool = True,
                      mark_as_read: bool = False,
                      days_limit: int | None = None,
                      limit: int = 10
                      ) -> list[dict]:
    """
    Connects to the email server and fetches emails
    from a specific sender using OAuth 2.0.
    Returns a list of dictionaries, each containing 'uid', 'message_id', 'sent_date' and 'message'.
    """
    if not config.email_senders:
        ## avoid fetching emails unless there is a email_from set up.
        return []

    messages = []
    creds = get_credentials()
    auth_string = f"user={config.email_account}\1auth=Bearer {creds.token}\1\1"

    assert config.email_server_url is not None, "Email server URL is None"
    
    with imaplib.IMAP4_SSL(config.email_server_url) as mailserver:
        mailserver.authenticate("XOAUTH2", lambda x: auth_string.encode("utf-8"))
        mailserver.select("inbox")

        search_criteria = format_search_criteria(only_unseen, days_limit, config.email_senders)
        logger.info(f"Search criteria: {search_criteria}")
        
        result, data = mailserver.uid("search", search_criteria) # mailserver.uid("search", None, search_criteria)
        if result != "OK":
            logger.error(f"Search failed with result: {result}")
            return []
        
        email_ids = distill_email_ids(data, limit, reverse=False)
        logger.info(f"Fetched {len(email_ids)} email IDs")
        
        for id in email_ids:
            result, msg_data = mailserver.uid("fetch", id, "(BODY.PEEK[])")
            if result != "OK":
                logger.error(f"Fetch failed for ID {id}")
                continue

            ## let's convert the msg_data to a email.message.Message object
            msg_data = email.message_from_bytes(msg_data[0][1])
            messages.append(msg_data)
            
            if mark_as_read:
                mailserver.uid("store", id, "+FLAGS", "\\Seen")
    
    return messages

def distill_new_emails_from_latest(latest_emails: list[Message]
                                   ) -> list[Message]:
    """ Distills the new emails from the latest emails """
    return [x for x in latest_emails if not does_email_exist(get_email_uid(x))]

def add_email_to_database(email: Message,
                          db: SQLiteWrapper,
                          ) -> int:
    """ Adds an email to the database """
    create_dict = format_email_dict(email)
    email_id = db.create('Email', create_dict)
    return email_id

## -------------------------
def format_email_dict(email: Message) -> dict:
    """Formats the email data into a dictionary."""
    email_uid = get_email_uid(email)
    sent_date = get_email_sent_date(email) 
    # Extract the body text from the email
    body = ""
    if email.is_multipart():
        # For multipart messages, iterate through parts
        for part in email.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Skip any attachments
            if "attachment" in content_disposition:
                continue
            
            # Get text/plain parts
            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    assert isinstance(payload, bytes), "Expected bytes payload for text/plain part"
                    body = payload.decode("utf-8", errors="ignore")
                    break  # Use the first text/plain part
                except Exception as e:
                    pass
            # Fallback to text/html if no text/plain found
            elif content_type == "text/html" and not body:
                try:
                    payload = part.get_payload(decode=True)
                    assert isinstance(payload, bytes), "Expected bytes payload for text/plain part"
                    body = payload.decode('utf-8', errors='ignore')
                except Exception as e:
                    pass
    else:
        # For non-multipart messages
        try:
            payload = email.get_payload(decode=True)
            assert isinstance(payload, bytes), "Expected bytes payload for text/plain part"
            body = payload.decode("utf-8", errors="ignore")
        except Exception as e:
            body = str(email.get_payload())
    
    return {
        "email_uid": email_uid,
        "sent_date": sent_date,
        "subject": email.get("Subject"),
        "body": body,
    }

def format_search_criteria(only_unseen: bool = True, 
                           days_limit: int | None = None, 
                           from_emails: List[str] = []
                           ) -> str:
    """Formats the search criteria for the email server."""
    search_criteria_parts = []
    
    try:
        if only_unseen:
            search_criteria_parts.append("UNSEEN")
        
        if from_emails:
            if len(from_emails) == 1:
                # If there's only one email, create a simple FROM query
                search_criteria_parts.append(f'FROM "{from_emails[0]}"')
            elif len(from_emails) > 1:
                # If there are multiple emails, create an OR query
                from_parts = [f'FROM "{email}"' for email in from_emails]
                search_criteria_parts.append(f"(OR {' '.join(from_parts)})")
        
        if days_limit:
            try:
                # Try to convert days_limit to a proper date format
                date = (datetime.now() - timedelta(days=days_limit)).strftime("%d-%b-%Y")
                search_criteria_parts.append(f'SINCE "{date}"')
            except Exception as e:
                logger.error(f"Error formatting date with days_limit={days_limit}: {e}")
                # Fallback: don't use the days_limit filter
    except Exception as e:
        logger.error(f"Error in format_search_criteria: {e}")
    
    result = f"({' '.join(search_criteria_parts)})"
    return result

def distill_email_ids(data: list[bytes], limit: int = 10, reverse: bool = True) -> list[str]:
    """Distills the email IDs from the search results."""
    email_ids = [x.decode() for x in data[0].split()]
    email_ids = email_ids[:limit]
    if reverse:
        email_ids.reverse()
    return email_ids

def get_email_uid(email: Message) -> str:
    """ Distills the email UUID the email msg."""
    email_uid = email.get("Message-ID")
    if email_uid is None:
        logger.warning("Message-ID is None, generating fallback ID")
        email_uid = f"unknown-{datetime.now().timestamp()}"
    
    return email_uid

def get_email_sent_date(email: Message) -> datetime:
    """ Gets the sent date from the email msg."""
    date_str = email.get("Date")
    if date_str is None:
        logger.warning("Date is None, using current time")
        return datetime.now()
    return parsedate_to_datetime(date_str)
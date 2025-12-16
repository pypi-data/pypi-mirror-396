import datetime
import logging
import os

from paper_inbox.modules.config.paths import get_database_filepath
from paper_inbox.modules.database.sqlwrapper import SQLiteWrapper
from paper_inbox.modules.loggers import setup_logger

logger = setup_logger('database', logging.INFO, False)

def does_database_exist() -> bool:
    """Checks if the database file exists."""
    database_filepath = get_database_filepath()
    return database_filepath.exists()

def get_database_handle(filename='db.sqlite3', delete_existing=False):
    db_filepath = get_database_filepath()

    ## if delete existing flag is set we delete it.
    if os.path.exists(db_filepath) and delete_existing:
        os.remove(db_filepath)

    ## now check if we should initialize the database
    db = SQLiteWrapper(db_filepath, debug=False)
    ## run the setup database, to build tables in case they don't exist.
    setup_database(db)

    return db

def setup_database(db: SQLiteWrapper):
    """Sets up the SQLite database and creates the emails table if it doesn't exist."""
    if not db.table_exists('emails'):
        db.create_entity_type('Email', {
            'email_uid': 'TEXT UNIQUE NOT NULL',
            'sent_date': 'TIMESTAMP NOT NULL',
            'subject': 'TEXT',
            'body': 'TEXT',
            'attachments': 'TEXT',
            'printed_at': 'TIMESTAMP',
            'printed': 'BOOLEAN DEFAULT FALSE'
        })
        logger.info("Created EMAILS table")

##  
def does_email_exist(email_uid: str) -> bool:
    """Checks if an email exists in the database."""
    db = get_database_handle()
    result = db.find_one('Email', [['email_uid', 'is', email_uid]])
    return result is not None

def get_email_from_db_by_id(email_id: int) -> dict:
    """Gets an email by its ID."""
    db = get_database_handle()
    result = db.find_one('Email', [['id', 'is', email_id]])
    return result

def get_unprinted_emails() -> list[dict]:
    """Gets emails that are not printed yet."""
    db = get_database_handle()
    result = db.find('Email', [['printed', 'is', False]])
    return result

def set_all_emails_as_printed():
    """Sets all the emails in the database as printed."""
    db = get_database_handle()
    all_emails = db.find('Email', [], ['id'])
    all_ids = [email.get('id') for email in all_emails]
    for id in all_ids:
        set_email_as_printed(id)

def set_email_as_printed(email_id: int):
    """Sets an email as printed."""
    db = get_database_handle()
    update_dict = {
        'printed': True,
        'printed_at': datetime.datetime.now() 
    }
    db.update('Email', email_id, update_dict)

def get_email_from_db_by_uid(email_uid: str) -> dict:
    """Gets an email by its message ID."""
    db = get_database_handle()
    result = db.find_one('Email', [['email_uid', 'is', email_uid]])
    return result

def update_email_attachments(email_id: int, attachments: list[str]):
    """Updates an email's attachments."""
    db = get_database_handle()
    db.update('Email', email_id, {'attachments': ",".join(attachments)})

def save_email_to_db(email_dict: dict):
    """Saves an email to the database."""
    db = get_database_handle()
    return db.create('Email', email_dict)

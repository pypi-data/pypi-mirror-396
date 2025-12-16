import os
import re


def is_valid_client_secrets_path(filepath: str) -> bool:
    if not os.path.exists(filepath):
        return False
    if not os.path.isfile(filepath):
        return False
    return True

def is_valid_email_address(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_valid_email_addresses(emails: list[str]) -> bool:
    for email in emails:
        if not is_valid_email_address(email):
            return False
    return True
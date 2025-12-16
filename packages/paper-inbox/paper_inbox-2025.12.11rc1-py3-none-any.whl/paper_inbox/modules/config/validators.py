from paper_inbox.modules.config.file import get_config


def has_email_account_defined() -> bool:
    config = get_config()
    return config.get("EMAIL_ACCOUNT") is not None and config.get("EMAIL_ACCOUNT") != ""

def has_sender_emails_defined() -> bool:
    config = get_config()
    return config.get("EMAIL_FROM") is not None and config.get("EMAIL_FROM") != []

def has_trusted_network_defined() -> bool:
    config = get_config()
    return config.get("TRUSTED_SSIDS") is not None and config.get("TRUSTED_SSIDS") != []
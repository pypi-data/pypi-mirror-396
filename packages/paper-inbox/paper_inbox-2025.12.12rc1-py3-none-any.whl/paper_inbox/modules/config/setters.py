from paper_inbox.modules.config.file import get_config, write_config


def set_email_account(email: str):
    update_dict = {
        "EMAIL_ACCOUNT": email
    }
    write_config(update_dict, merge=True)

def add_from_email(email: str) -> bool:
    from_emails = get_config().get("EMAIL_FROM")
    if from_emails is None:
        from_emails = []
    from_emails.append(email)
    update_dict = {
        "EMAIL_FROM": from_emails
    }
    write_config(update_dict, merge=True)
    return True

def add_trusted_network(ssid: str) -> bool:
    trusted_networks = get_config().get("TRUSTED_SSIDS")
    if trusted_networks is None:
        trusted_networks = []
    trusted_networks.append(ssid)
    update_dict = {
        "TRUSTED_SSIDS": trusted_networks
    }
    write_config(update_dict, merge=True)
    return True

def set_telegram_bot_token(token: str) -> bool:
    update_dict = {
        "TELEGRAM_BOT_TOKEN": token
    }
    write_config(update_dict, merge=True)
    return True

def set_telegram_chat_id(chat_id: str) -> bool:
    update_dict = {
        "TELEGRAM_CHAT_ID": chat_id
    }
    write_config(update_dict, merge=True)
    return True

def set_send_telegram_notifications(send: bool) -> bool:
    update_dict = {
        "SEND_TELEGRAM_NOTIFICATIONS": send
    }
    write_config(update_dict, merge=True)
    return True
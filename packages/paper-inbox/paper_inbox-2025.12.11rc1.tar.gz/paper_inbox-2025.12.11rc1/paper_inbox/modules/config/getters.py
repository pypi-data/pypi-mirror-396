import os
import shutil

from paper_inbox.modules.config.file import get_config

CONFIG = get_config()

telegram_bot_token: str | None = CONFIG.get("TELEGRAM_BOT_TOKEN")
telegram_chat_id: str | None = CONFIG.get("TELEGRAM_CHAT_ID")
_has_token: bool = bool(telegram_bot_token)
_has_chatID: bool = bool(telegram_chat_id)
_send_telegram: bool = bool(CONFIG.get("SEND_TELEGRAM_NOTIFICATIONS"))
send_telegram_notifications: bool = (_has_token and _has_chatID and _send_telegram)


## some printer timeout settings
printer_timeout_seconds: int = 300
printer_poll_interval_seconds: float = 1.0

## network retry settings
network_retry_max_retries: int = 3
network_retry_delay: int = 10

## network auth
trusted_ssids: list[str] | None = CONFIG.get("TRUSTED_SSIDS")
email_account: str | None = CONFIG.get("EMAIL_ACCOUNT")
email_senders: list[str] | None = CONFIG.get("EMAIL_FROM")
email_server_url: str | None = CONFIG.get("IMAP_SERVER")

## not linked into the config file yet ----------------------------------------------------
## Paths to external dependencies
cups_path: str | None = os.getenv("LPSTAT_PATH") or shutil.which("lpstat")
libreoffice_path: str | None = os.getenv("LIBREOFFICE_PATH") or shutil.which("libreoffice")
## while developing, we can print only the first page of the email
print_only_first_page: bool = False 

## while developing, we can skip the printing part and just return True
skip_printing_irl: bool = False

## force grayscale printing
force_grayscale: bool = True

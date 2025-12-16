import logging

import requests

from paper_inbox.modules import config
from paper_inbox.modules.loggers import setup_logger
from paper_inbox.modules.utils import retry_on_failure

logger = setup_logger('telegram', logging.INFO, False)

@retry_on_failure()
def send_telegram_notification(msg: str):
    if not config.send_telegram_notifications:
        return 
    send_msg(msg)

def send_msg(msg: str):
    url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    data = {
        'chat_id': config.telegram_chat_id,
        'text': msg,
        'parse_mode': 'html'
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logger.info("Telegram message sent successfully.")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error sending Telegram message: {e}")
        if e.response:
            logger.error(f"Error response from Telegram API: {e.response.text}")
        return None
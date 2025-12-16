import tomli
import tomli_w

from paper_inbox.modules.config.paths import get_config_filepath


def init_config():
    # Define the default structure and values for your config
    config = {}
    config["EMAIL_ACCOUNT"] = "" ## your_email@example.com
    config["EMAIL_FROM"] = [] ## ["sender@school.com", "sender@work.com"]
    config["IMAP_SERVER"] = "imap.gmail.com"
    config["TRUSTED_SSIDS"] = [] ## ["school_wifi", "work_wifi"]
    config["SEND_TELEGRAM_NOTIFICATIONS"] = False
    config["TELEGRAM_BOT_TOKEN"] = ""
    config["TELEGRAM_CHAT_ID"] = ""

    # Write the default config to the file and return it
    success = write_config(config)
    return success

def get_config() -> dict:
    """
    Reads the config from the TOML file.
    If the file doesn't exist, it creates a default one and returns it.
    """
    config_path = get_config_filepath()
    if not config_path.exists():
        return {} ## return an empty dictionary if the file doesn't exist
    
    # If the file exists, open it in binary read mode and load the TOML
    with open(config_path, "rb") as f:
        return tomli.load(f)
    
def write_config(config: dict, merge: bool = True):
    """
    Writes a dictionary to the TOML config file.
    If merge=True, updates existing config rather than replacing it.
    """
    config_path = get_config_filepath()
    
    if merge and config_path.exists():
        # Read existing config
        with open(config_path, "rb") as f:
            existing_config = tomli.load(f)
        # Update with new values (shallow merge)
        existing_config.update(config)
        config = existing_config
    
    # Write the config
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)

    return True
import logging
import time

from paper_inbox.modules import config
from paper_inbox.modules.loggers import setup_logger
from paper_inbox.modules.printer import cups
from paper_inbox.modules.utils import is_on_home_network

logger = setup_logger('printer', logging.INFO, False)

def get_printer() -> str | None:
    """
    Get the default printer from CUPS.
    """
    queues = cups.get_cups_queues()
    if len(queues) == 0:
        return None
    return queues[0]

def print_file(filepath: str) -> bool:
    """ Builds basic cups command to print a file, submits and waits for successful completion """
    if config.skip_printing_irl:
        time.sleep(1) ## sleep for 1 second to simulate the printing time
        return False
    
    if not is_on_home_network():
        logger.warning("Not on a trusted Wi-Fi network. Skipping print job.")
        return False

    printer = get_printer()
    assert printer is not None, "No printer found"

    cmd = cups.build_cmd(printer, filepath)
    job_id, _ = cups.submit_job(cmd)
    if not job_id:
        return False
    return cups.await_for_completion(job_id)



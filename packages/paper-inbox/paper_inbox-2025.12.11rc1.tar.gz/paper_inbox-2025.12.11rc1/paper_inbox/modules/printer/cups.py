import logging
import re
import subprocess
import time

from paper_inbox.modules import config
from paper_inbox.modules.loggers import setup_logger

logger = setup_logger('printer', logging.INFO, False)

def get_cups_queues() -> list[str]:
    """
    Returns a list of CUPS queues by parsing `lpstat -e`.
    """
    try:
        res = subprocess.run(["lpstat", "-e"], capture_output=True, text=True, check=False)
        return [ln.strip() for ln in (res.stdout or "").splitlines() if ln.strip()]
    except FileNotFoundError:
        logger.info("CUPS tools not found. Install cups/cups-client.")
        return []

def build_cmd(destination: str,
              filepath: str,
              copies: int = 1,
              first_page_only: bool = False,
              black_and_white: bool | None = None,
              title: str | None = None,
              document_format: str | None = None,
              extra_options: dict[str, str] | None = None,
              ) -> list[str]:
    """
    Build the `lp` command for CUPS without executing it.
    """
    cmd = ["lp", "-d", destination, "-n", str(copies)]
    if title:
        cmd += ["-t", title]
    if first_page_only or config.print_only_first_page:
        cmd += ["-o", "page-ranges=1"]
    if black_and_white is True or config.force_grayscale:
        cmd += ["-o", "print-color-mode=monochrome", "-o", "ColorModel=Gray"]
    elif black_and_white is False:
        cmd += ["-o", "print-color-mode=color", "-o", "ColorModel=RGB"]
    if document_format:
        cmd += ["-o", f"document-format={document_format}"]
    if extra_options:
        for k, v in extra_options.items():
            cmd += ["-o", f"{k}={v}"]
    cmd.append(filepath)
    return cmd

def submit_job(cmd: list[str]
               ) -> tuple[str | None, str]:
    """
    Submit the job to CUPS. Returns (job_id, combined_output).
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        logger.info("The 'lp' command was not found. Please install CUPS ('cups' and 'cups-client').")
        return None, ""
    out = (result.stdout or "") + "\n" + (result.stderr or "")
    if result.returncode != 0:
        logger.info(f"CUPS lp failed (code {result.returncode}).")
        if result.stdout:
            logger.info(result.stdout.strip())
        if result.stderr:
            logger.info(result.stderr.strip())
        return None, out
    m = re.search(r"request id is (\S+)", out, re.IGNORECASE)
    job_id = m.group(1) if m else None
    return job_id, out

def await_for_completion(job_id: str, 
                         ) -> bool:
    """
    Poll CUPS until job leaves not-completed and verify it's listed as completed.
    """
    timeout_sec = config.printer_timeout_seconds
    poll_interval_sec = config.printer_poll_interval_seconds
    logger.info(f"Submitted CUPS job: {job_id}. Waiting for completion (timeout {timeout_sec}s)...")
    start = time.time()
    while True:
        try:
            st = subprocess.run(
                ["lpstat", "-W", "not-completed", "-o"],
                capture_output=True, text=True, check=False
            )
        except FileNotFoundError:
            logger.info("The 'lpstat' command was not found. Please install CUPS client tools.")
            return False
        if job_id not in (st.stdout or ""):
            break
        if time.time() - start > timeout_sec:
            logger.info(f"Timed out waiting for job {job_id} to complete.")
            return False
        time.sleep(poll_interval_sec)

    try:
        st2 = subprocess.run(
            ["lpstat", "-W", "completed", "-o"],
            capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        logger.info("The 'lpstat' command was not found. Please install CUPS client tools.")
        return False

    if job_id in (st2.stdout or ""):
        logger.info(f"Job {job_id} completed successfully.")
        return True

    logger.info(f"Job {job_id} is no longer pending but not listed as completed; likely canceled/aborted.")
    return False
import shutil
import subprocess
import time

from paper_inbox import CLI_ENTRY_POINT
from paper_inbox.modules.const import BEAT
from paper_inbox.modules.tui.utils import spinner


@spinner("Checking for cron schedule...")
def find_cron_schedule():
    """
    Check if a cron job exists for this project.
    Returns the cron schedule string if found, or None if not found.
    """
    time.sleep(BEAT)
        
    try:
        # Run crontab -l to list all cron jobs
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # If no cron jobs exist, crontab returns exit code 1
        if result.returncode != 0:
            return None
        
        # Look for cron jobs containing "simple_calculator.py" (this project's entry point)
        for line in result.stdout.strip().split('\n'):
            if line and CLI_ENTRY_POINT in line and not line.strip().startswith('#'):
                # Extract the cron schedule (first 5 fields)
                # Format: "MIN HOUR DAY MONTH WEEKDAY command"
                parts = line.split()
                if len(parts) >= 5:
                    # Return the cron schedule part (first 5 fields)
                    cron_schedule = ' '.join(parts[:5])
                    return cron_schedule
        
        # No matching cron job found
        return None
        
    except FileNotFoundError:
        # crontab command not available
        return None
    except Exception:
        # Other errors
        return None

@spinner("Setting up cron schedule...")
def set_cron_schedule(cron_schedule: str):
    """
    Set up a cron job with the given schedule.
    
    Args:
        cron_schedule: Cron schedule string (e.g., "0 */4 * * *" for every 4 hours)
    
    Returns:
        True if successful, False otherwise
    """
    time.sleep(BEAT * 4)
    
    try:
        from paper_inbox.modules.config.paths import get_log_dir
        ## get the bin to this app.
        bin_path = shutil.which(CLI_ENTRY_POINT)
        cron_line = f"{cron_schedule} {bin_path} >> {get_log_dir()}/cron.log 2>&1"
        
        # Get existing crontab
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Filter out existing cron jobs for this project
        existing_crons = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                # Keep all lines except those containing the CLI entry point
                if line and CLI_ENTRY_POINT not in line:
                    existing_crons.append(line)
        
        # Add the new cron line
        existing_crons.append(cron_line)
        
        # Set the new crontab
        new_crontab = '\n'.join(existing_crons) + '\n'
        result = subprocess.run(
            ["crontab", "-"],
            input=new_crontab,
            text=True,
            capture_output=True,
            check=False
        )
        
        return result.returncode == 0
        
    except FileNotFoundError:
        # crontab command not available
        return False
    except Exception:
        # Other errors
        return False

@spinner("Removing cron schedule...")
def remove_cron_schedule():
    """
    Remove the cron job for this project.
    
    Returns:
        True if successful, False otherwise
    """
    time.sleep(BEAT * 2)
    
    try:
        # Get existing crontab
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # If no crontab exists, nothing to remove (success)
        if result.returncode != 0:
            return True
        
        # Filter out cron jobs for this project (containing "calc run")
        filtered_crons = []
        for line in result.stdout.strip().split('\n'):
            # Keep all lines except those containing the CLI entry point
            if line and CLI_ENTRY_POINT not in line:
                filtered_crons.append(line)
        
        # Set the new crontab (without the project's cron job)
        new_crontab = '\n'.join(filtered_crons) + '\n' if filtered_crons else ''
        result = subprocess.run(
            ["crontab", "-"],
            input=new_crontab,
            text=True,
            capture_output=True,
            check=False
        )
        
        return result.returncode == 0
        
    except FileNotFoundError:
        # crontab command not available
        return False
    except Exception:
        # Other errors
        return False
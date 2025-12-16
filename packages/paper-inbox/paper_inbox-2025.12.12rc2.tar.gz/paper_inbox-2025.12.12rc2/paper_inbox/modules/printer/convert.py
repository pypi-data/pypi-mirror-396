import logging
import os
import subprocess
import sys

from paper_inbox.modules import config
from paper_inbox.modules.loggers import setup_logger

logger = setup_logger('printer', logging.INFO, False)

def html_to_pdf(html_filepath: str, output_filepath: str) -> str | None:
    """ Converts an HTML file to a PDF using LibreOffice (in order to make them printable by CUPS) """
    if not config.libreoffice_path:
        logger.error("LibreOffice path not configured. Cannot convert .html file.")
        sys.exit(1)
    
    output_dir = os.path.dirname(output_filepath)
    
    try:
        cmd: list[str] = [
            str(config.libreoffice_path),
            "--headless",
            "--writer",
            "--convert-to",
            "pdf",
            html_filepath,
            "--outdir",
            output_dir
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)
        if result.returncode != 0:
            logger.error(f"libreoffice failed to convert html (code {result.returncode}): {result.stderr}")
            return None

        # LibreOffice will create a PDF with the same base name, e.g., tempfile.html -> tempfile.pdf
        # We need to rename it to our desired output_filepath.
        filename = os.path.basename(html_filepath).lower().replace('.html', '.pdf')
        generated_pdf_path = os.path.join(output_dir, filename)
        if os.path.exists(generated_pdf_path):
            os.rename(generated_pdf_path, output_filepath)
            logger.info(f"Successfully converted {html_filepath} to {output_filepath}")
            return output_filepath
        else:
            logger.error(f"Conversion of {html_filepath} seemed to succeed, but PDF file not found.")
            return None

    except FileNotFoundError:
        logger.error(f"libreoffice not found at '{config.libreoffice_path}'. Please install it or check the path.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        logger.error("Timeout converting .html to .pdf with libreoffice.")
        return None

def docx_to_pdf(docx_path: str) -> str | None:
    """Converts a DOCX file to PDF using LibreOffice (in order to make them printable by CUPS)"""
    if not config.libreoffice_path:
        logger.error("LibreOffice path not configured. Cannot convert .docx file.")
        return None

    output_dir = os.path.dirname(docx_path)
    try:
        cmd = [
            config.libreoffice_path,
            "--headless",
            "--convert-to",
            "pdf",
            docx_path,
            "--outdir",
            output_dir
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)
        if result.returncode != 0:
            logger.error(f"libreoffice failed (code {result.returncode}): {result.stderr}")
            return None
        
        pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
        if os.path.exists(pdf_path):
            logger.info(f"Successfully converted {docx_path} to {pdf_path}")
            return pdf_path
        else:
            logger.error(f"Conversion of {docx_path} seemed to succeed, but PDF file not found.")
            return None

    except FileNotFoundError:
        logger.error(f"libreoffice not found at '{config.libreoffice_path}'. Please install it or check the path.")
        return None
    except subprocess.TimeoutExpired:
        logger.error("Timeout converting .docx to .pdf with libreoffice.")
        return None
    
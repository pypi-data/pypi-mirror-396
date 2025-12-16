from __future__ import annotations

import os
import shutil
import subprocess
import typing as t
from pathlib import Path

from paper_inbox.modules.pdf import exceptions, validators

if t.TYPE_CHECKING:
    from pathlib import Path

def validate_pdfs(files: list[Path]):
    ## filter the files to only keep the pdfs.
    pdf_files = [x for x in files if Path(x).suffix.lower()=='.pdf']
    ## run through the attachments and fix them if canva or syntax error.
    to_fix = [x for x in pdf_files if is_canva(x) or not is_valid(x)]
    for item in to_fix:
        fix_pdf(item)


def is_canva(filepath: str | Path) -> bool:
    info = info_as_dict(filepath)
    creator = info.get('Creator', None)
    producer = info.get('Producer', None)
    if creator and creator.lower()=='canva':
        return True
    if producer and producer.lower()=='canva':
        return True
    return False

def is_valid(filepath: str | Path) -> bool:
    """ validates the PDF to make sure it conforms and will be printable """
    try:
        validators.validate_magic_header(filepath)
        validators.validate_file_head(filepath)
        validators.validate_structure(filepath)
        validators.validate_not_html(filepath)
        validators.validate_mime_type(filepath)
        return True
    except exceptions.PDFError as e:
        return False

def info_as_string(filepath: str | Path) -> str:
    """ returns string stderr + stdout of the 'pdfinfo' call"""
    result = subprocess.run(["pdfinfo", filepath], capture_output=True, text=True)

    ## combine the stderr and stdout for full context.
    return result.stdout + result.stderr

def info_as_dict(filepath: str | Path) -> dict:
    """ returns a dictionary of the 'pdfinfo' out"""
    raw = info_as_string(filepath)

    info = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()

    return info


def fix_pdf(input_path: str | Path) -> bool:
    """ attempts to fix malformed pdfs by re-exporting using libreoffice """
    if isinstance(input_path, str):
        input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF does not exist: {input_path}")
    
    ## create subdir, as libreoffice will use same name.
    input_dir = input_path.parent
    output_dir = input_dir / 'fix' 
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / input_path.name
    ## set up a path for the original pdf to stay after conversion
    backup_path = input_dir / (input_path.stem + '_original.pdf')

    ## run the pdf through libreoffice
    cmd = [
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        str(input_path)
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice failed:\nSTDOUT:\n{result.stdout.decode()}\nSTDERR:\n{result.stderr.decode()}"
        )

    ## check if the 'fixed' pdf is valid
    valid = is_valid(output_path)
    if not valid: ## cleanup and return False
        output_path.unlink()
        output_dir.rmdir()
        return False

    ## copy original file to backup 
    shutil.copyfile(input_path, backup_path)
    ## overwrite original input_path
    os.replace(output_path, input_path)
    output_dir.rmdir()

    return True
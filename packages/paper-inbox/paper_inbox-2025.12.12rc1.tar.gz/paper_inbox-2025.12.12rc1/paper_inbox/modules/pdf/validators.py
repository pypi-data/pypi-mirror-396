from __future__ import annotations

import subprocess
import typing as t

from paper_inbox.modules.pdf import exceptions

if t.TYPE_CHECKING:
    from pathlib import Path

def validate_magic_header(filepath: str | Path) -> None:
    """ uses 'file' cli to check the magic header on the file """
    result = subprocess.check_output(["file", filepath], text=True)
    expected = ': PDF document, version 1.'

    if expected not in result:
        raise exceptions.MalformedMagicHeader(result, expected)
    
def validate_file_head(filepath: str | Path) -> None:
    """ uses the 'head' cli to check the head of the file"""
    result = subprocess.check_output(["head", "-n", "1", filepath], text=True)
    expected = '%PDF-1.'

    if expected not in result:
        raise exceptions.MalformedFileHead(result, expected)
    
def validate_structure(filepath: str | Path) -> None:
    """ uses the 'pdfinfo' cli to check for any (syntax) errors in pdf structure """
    res = subprocess.run(["pdfinfo", filepath], capture_output=True, text=True)
    result = res.stderr + res.stdout

    if 'Syntax Error' in result or 'Syntax Warning' in result:
        raise exceptions.SyntaxErrorInPDFStructure(result)
    if 'Error' in result:
        raise exceptions.ErrorInPDFStructure(result)
    
def validate_not_html(filepath: str | Path) -> None:
    """Validates that the file is not actually an HTML error page."""
    with open(filepath, "rb") as f:
        head = f.read(8192)  # bytes, no decoding

    unwanted_markers = [
        b"<!DOCTYPE html",
        b"<html",
        b"<HTML",
    ]

    for marker in unwanted_markers:
        if marker in head:
            raise exceptions.InvalidDataTypeHTML(head)

def validate_mime_type(filepath: str | Path) -> None:
    """ uses the 'mimetype' cli command """
    result = subprocess.check_output(["mimetype", filepath], text=True)
    expected = 'application/pdf'

    if expected not in result:
        raise exceptions.InvalidMimeType(result, expected)
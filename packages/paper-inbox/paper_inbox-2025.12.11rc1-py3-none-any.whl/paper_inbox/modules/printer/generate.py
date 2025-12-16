import html as _html
import logging
import os
import tempfile
from datetime import datetime

from paper_inbox.modules.loggers import setup_logger
from paper_inbox.modules.printer import convert

logger = setup_logger('printer', logging.INFO, False)

def generate_email_pdf(email: dict, email_dir: str) -> str | None:
    """
    Generates a pdf from an email, by first building it up
    as a HTML file, then converting to PDF.
    """
    temp_html_filepath = generate_temporary_email_html_file(email)
    output_filepath = os.path.join(email_dir, "email.pdf")
    pdf_filepath = convert.html_to_pdf(temp_html_filepath, output_filepath)
    return pdf_filepath

def generate_temporary_email_html_file(email: dict, include_header: bool = True) -> str:
    """
    Generates the HTML content for an email.
    """
    subject = email.get('subject') or ''
    sent_date_int = email.get('sent_date') or 0
    sent_date = datetime.fromtimestamp(sent_date_int).strftime('%Y-%m-%d %H:%M:%S') if sent_date_int else ''
    email_id = email.get('id')
    body = email.get('body') or ''
    ## attachments are stored as a comma-separated list of filenames in the database.
    attachments = email.get('attachments') or ''
    attachments_html = ""
    if attachments:
        attachments_html = "<ul>" + "".join([f"<li>{_html.escape(filename)}</li>" for filename in attachments.split(',')]) + "</ul>"

    header_html = ""
    if include_header:
        header_html = f"""
        <div style="font-family: system-ui, sans-serif; font-size: 12pt; margin-bottom: 12px;">
          <div><strong>Subject:</strong> {_html.escape(subject)}</div>
          <div><strong>Sent:</strong> {_html.escape(str(sent_date))}</div>
          <div><strong>ID:</strong> {_html.escape(str(email_id))}</div>
          <div><strong>Attachments:</strong> {attachments_html}</div>
          <hr />
        </div>
        """

    looks_like_html = '<' in body and '>' in body
    body_html = body if looks_like_html else f"<pre style='white-space: pre-wrap; font: 18pt monospace;'>{_html.escape(body)}</pre>"

    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>{_html.escape(subject) if subject else 'Email'}</title>
<style>
  @page {{ margin: 12mm; }}
  body {{ margin: 0; padding: 1.5rem; }}
</style>
</head>
<body>
{header_html}
{body_html}
</body>
</html>"""
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    temp.write(html_doc.encode('utf-8'))
    temp.close()
    return temp.name

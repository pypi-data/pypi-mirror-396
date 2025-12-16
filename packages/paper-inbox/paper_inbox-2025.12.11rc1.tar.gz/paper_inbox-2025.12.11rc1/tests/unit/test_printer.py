# tests/test_printer.py
"""Tests for printer module"""
import os  # <-- Add this import
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from paper_inbox.modules.printer.convert import docx_to_pdf, html_to_pdf
from paper_inbox.modules.printer.utils import get_printer, print_file


class TestPrinterUtils:
    """Test printer utility functions"""
    
    def test_get_printer_returns_first_queue(self):
        """Test getting printer returns first queue"""
        with patch('paper_inbox.modules.printer.cups.get_cups_queues') as mock_queues:
            mock_queues.return_value = ['Printer1', 'Printer2']
            
            result = get_printer()
            assert result == 'Printer1'
    
    def test_get_printer_returns_none_when_no_queues(self):
        """Test getting printer returns None when no queues"""
        with patch('paper_inbox.modules.printer.cups.get_cups_queues') as mock_queues:
            mock_queues.return_value = []
            
            result = get_printer()
            assert result is None
    
    def test_print_file_skips_when_skip_printing_enabled(self):
        """Test print_file skips when skip_printing_irl is True"""
        with patch('paper_inbox.modules.config.skip_printing_irl', True):
            result = print_file('/path/to/file.pdf')
            assert result is False
    
    def test_print_file_skips_when_not_on_home_network(self):
        """Test print_file skips when not on trusted network"""
        with patch('paper_inbox.modules.config.skip_printing_irl', False):
            with patch('paper_inbox.modules.utils.is_on_home_network') as mock_network:
                mock_network.return_value = False
                
                result = print_file('/path/to/file.pdf')
                assert result is False
    
    def test_print_file_submits_job_when_on_home_network(self):
        """Test print_file submits job when on home network"""
        with patch('paper_inbox.modules.config.skip_printing_irl', False):
            # Patch where is_on_home_network is imported and used in printer.utils
            with patch('paper_inbox.modules.printer.utils.is_on_home_network', return_value=True):
                with patch('paper_inbox.modules.printer.utils.get_printer', return_value='TestPrinter'):
                    with patch('paper_inbox.modules.printer.cups.build_cmd', return_value=['lp', 'test']):
                        with patch('paper_inbox.modules.printer.cups.submit_job', return_value=(123, None)):
                            with patch('paper_inbox.modules.printer.cups.await_for_completion', return_value=True):
                                result = print_file('/path/to/file.pdf')
                                assert result is True


class TestPrinterConvert:
    """Test printer conversion functions"""
    
    def test_docx_to_pdf_returns_none_when_no_libreoffice(self):
        """Test docx_to_pdf returns None when LibreOffice not available"""
        with patch('paper_inbox.modules.config.libreoffice_path', None):
            result = docx_to_pdf('/path/to/file.docx')
            assert result is None
    
    def test_docx_to_pdf_success(self):
        """Test successful docx to pdf conversion"""
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = os.path.join(tmpdir, 'test.docx')
            pdf_path = os.path.join(tmpdir, 'test.pdf')
            
            # Create dummy docx file
            open(docx_path, 'w').close()
            
            with patch('paper_inbox.modules.config.libreoffice_path', '/usr/bin/libreoffice'):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    
                    # Create the expected PDF file
                    open(pdf_path, 'w').close()
                    
                    result = docx_to_pdf(docx_path)
                    assert result == pdf_path
    
    def test_html_to_pdf_returns_none_when_no_libreoffice(self):
        """Test html_to_pdf returns None when LibreOffice not available"""
        with patch('paper_inbox.modules.config.libreoffice_path', None):
            with pytest.raises(SystemExit):
                html_to_pdf('/path/to/file.html', '/path/to/output.pdf')
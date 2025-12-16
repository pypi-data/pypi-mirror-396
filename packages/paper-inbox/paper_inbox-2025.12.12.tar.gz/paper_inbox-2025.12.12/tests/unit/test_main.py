# tests/test_main.py
"""Tests for main application logic"""
from unittest.mock import MagicMock, patch

import pytest

from paper_inbox.main import (
    check_emails,
    print_emails,
    validate_auth,
    validate_config,
    validate_dependencies,
)


class TestMainValidation:
    """Test validation functions"""
    
    def test_validate_dependencies_exits_when_no_cups(self):
        """Test validation exits when CUPS not found"""
        with patch('paper_inbox.modules.config.cups_path', None):
            with pytest.raises(SystemExit):
                validate_dependencies()
    
    def test_validate_dependencies_exits_when_no_libreoffice(self):
        """Test validation exits when LibreOffice not found"""
        with patch('paper_inbox.modules.config.cups_path', '/usr/bin/lpstat'):
            with patch('paper_inbox.modules.config.libreoffice_path', None):
                with pytest.raises(SystemExit):
                    validate_dependencies()
    
    def test_validate_config_exits_when_no_email_account(self):
        """Test validation exits when no email account configured"""
        with patch('paper_inbox.modules.config.email_account', None):
            with pytest.raises(SystemExit):
                validate_config()
    
    def test_validate_config_exits_when_no_email_senders(self):
        """Test validation exits when no email senders configured"""
        with patch('paper_inbox.modules.config.email_account', 'test@example.com'):
            with patch('paper_inbox.modules.config.email_senders', None):
                with pytest.raises(SystemExit):
                    validate_config()
    
    def test_validate_auth_exits_when_no_refresh_token(self):
        """Test validation exits when no refresh token found"""
        with patch('paper_inbox.modules.tui.utils.does_refresh_token_file_exist', return_value=False):
            with pytest.raises(SystemExit):
                validate_auth()


class TestEmailChecking:
    """Test email checking functionality"""
    
    def test_check_emails_returns_zero_when_no_new_emails(self):
        """Test check_emails returns zero counts when no new emails"""
        # Need to patch where the functions are imported in main.py
        with patch('paper_inbox.main.get_database_handle'):
            with patch('paper_inbox.main.fetch_latest_emails', return_value=[]):
                fetch_count, new_count = check_emails(initial_run=False)
                assert fetch_count == 0
                assert new_count == 0
    
    def test_check_emails_sets_all_printed_on_initial_run(self):
        """Test check_emails sets all emails as printed on initial run"""
        mock_email = MagicMock()
        mock_email.get.return_value = 'Test Subject'
        
        # Patch at the location where functions are imported in main.py
        with patch('paper_inbox.main.get_database_handle'):
            with patch('paper_inbox.main.fetch_latest_emails', return_value=[mock_email]):
                with patch('paper_inbox.main.distill_new_emails_from_latest', return_value=[mock_email]):
                    with patch('paper_inbox.main.add_email_to_database', return_value=1):
                        with patch('paper_inbox.main.download_attachments', return_value=[]):
                            with patch('paper_inbox.main.update_email_attachments'):
                                with patch('paper_inbox.main.download_email'):
                                    with patch('paper_inbox.main.set_all_emails_as_printed') as mock_set_all:
                                        check_emails(initial_run=True)
                                        mock_set_all.assert_called_once()


class TestPrintEmails:
    """Test email printing functionality"""
    
    def test_print_emails_returns_zero_when_no_unprinted(self):
        """Test print_emails returns zero when no unprinted emails"""
        with patch('paper_inbox.main.get_unprinted_emails', return_value=[]):
            result = print_emails()
            assert result == 0
    
    def test_print_emails_limits_to_specified_count(self):
        """Test print_emails respects limit parameter"""
        mock_emails = [
            {'id': 1, 'subject': 'Email 1'},
            {'id': 2, 'subject': 'Email 2'},
            {'id': 3, 'subject': 'Email 3'},
        ]
        
        # Patch at the location where functions are imported in main.py
        with patch('paper_inbox.main.get_unprinted_emails', return_value=mock_emails):
            with patch('paper_inbox.main.get_email_from_db_by_id') as mock_get:
                mock_get.return_value = {'subject': 'Test', 'id': 1}
                # Need to return at least one file so the email gets "printed"
                with patch('paper_inbox.main.collect_files_to_print', return_value=['test.pdf']):
                    # Mock the print_file to return True (successful print)
                    with patch('paper_inbox.main.print_file', return_value=True):
                        with patch('paper_inbox.main.set_email_as_printed'):
                            with patch('paper_inbox.main.send_telegram_notification'):
                                with patch('paper_inbox.main.time.sleep'):  # Skip sleep delays
                                    result = print_emails(limit=2)
                                    # Should have printed 2 emails
                                    assert result == 2
                                    assert mock_get.call_count == 2
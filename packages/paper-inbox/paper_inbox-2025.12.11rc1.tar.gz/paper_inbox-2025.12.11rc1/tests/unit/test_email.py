# tests/test_email.py
"""Tests for email module"""
import tempfile
from datetime import datetime
from email.message import Message
from unittest.mock import patch

from paper_inbox.modules.email import (
    distill_email_ids,
    distill_new_emails_from_latest,
    download_attachments,
    format_email_dict,
    format_search_criteria,
    get_email_sent_date,
    get_email_uid,
)


class TestEmailFunctions:
    """Test email utility functions"""
    
    def test_format_search_criteria_unseen_only(self):
        """Test search criteria formatting with unseen only"""
        result = format_search_criteria(only_unseen=True)
        assert 'UNSEEN' in result
    
    def test_format_search_criteria_single_sender(self):
        """Test search criteria with single sender"""
        result = format_search_criteria(
            only_unseen=False,
            from_emails=['sender@example.com']
        )
        assert 'FROM "sender@example.com"' in result
    
    def test_format_search_criteria_multiple_senders(self):
        """Test search criteria with multiple senders"""
        result = format_search_criteria(
            only_unseen=False,
            from_emails=['sender1@example.com', 'sender2@example.com']
        )
        assert 'OR' in result
        assert 'FROM "sender1@example.com"' in result
        assert 'FROM "sender2@example.com"' in result
    
    def test_format_search_criteria_with_days_limit(self):
        """Test search criteria with days limit"""
        result = format_search_criteria(
            only_unseen=False,
            days_limit=7
        )
        assert 'SINCE' in result
    
    def test_distill_email_ids(self):
        """Test distilling email IDs from search results"""
        data = [b'1 2 3 4 5']
        result = distill_email_ids(data, limit=3, reverse=False)
        assert result == ['1', '2', '3']
    
    def test_distill_email_ids_with_reverse(self):
        """Test distilling email IDs with reverse"""
        data = [b'1 2 3']
        result = distill_email_ids(data, limit=10, reverse=True)
        assert result == ['3', '2', '1']
    
    def test_get_email_uid(self):
        """Test extracting email UID"""
        msg = Message()
        msg['Message-ID'] = '<test-123@example.com>'
        
        result = get_email_uid(msg)
        assert result == '<test-123@example.com>'
    
    def test_get_email_uid_fallback(self):
        """Test email UID fallback when Message-ID is None"""
        msg = Message()
        
        result = get_email_uid(msg)
        assert result.startswith('unknown-')
    
    def test_get_email_sent_date(self):
        """Test extracting email sent date"""
        msg = Message()
        msg['Date'] = 'Mon, 13 Nov 2023 10:00:00 +0000'
        
        result = get_email_sent_date(msg)
        assert isinstance(result, datetime)
    
    def test_get_email_sent_date_fallback(self):
        """Test email sent date fallback when Date is None"""
        msg = Message()
        
        result = get_email_sent_date(msg)
        assert isinstance(result, datetime)
        # Should be close to current time
        assert (datetime.now() - result).total_seconds() < 5
    
    def test_format_email_dict(self):
        """Test formatting email to dictionary"""
        msg = Message()
        msg['Message-ID'] = '<test@example.com>'
        msg['Date'] = 'Mon, 13 Nov 2023 10:00:00 +0000'
        msg['Subject'] = 'Test Subject'
        msg.set_payload('Test Body')
        
        result = format_email_dict(msg)
        
        assert result['email_uid'] == '<test@example.com>'
        assert result['subject'] == 'Test Subject'
        assert 'sent_date' in result
        assert 'body' in result
    
    def test_distill_new_emails_from_latest(self):
        """Test distilling new emails from latest"""
        msg1 = Message()
        msg1['Message-ID'] = '<new-email@example.com>'
        
        msg2 = Message()
        msg2['Message-ID'] = '<existing-email@example.com>'
        
        latest = [msg1, msg2]
        
        with patch('paper_inbox.modules.email.does_email_exist') as mock_exists:
            # First email is new, second exists
            mock_exists.side_effect = [False, True]
            
            result = distill_new_emails_from_latest(latest)
            assert len(result) == 1
            assert get_email_uid(result[0]) == '<new-email@example.com>'
    
    def test_download_attachments_with_pdf(self):
        """Test downloading PDF attachments"""
        msg = Message()
        msg.set_type('multipart/mixed')
        
        # Create attachment part
        attachment = Message()
        attachment.set_type('application/pdf')
        attachment.set_payload(b'PDF content')
        attachment.add_header('Content-Disposition', 'attachment', filename='test.pdf')
        msg.attach(attachment)
        
        with patch('paper_inbox.modules.utils.get_data_download_dir') as mock_dir:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_dir.return_value = tmpdir
                
                result = download_attachments(msg, 123)
                assert 'test.pdf' in result
    
    def test_download_attachments_no_attachments(self):
        """Test downloading attachments when none exist"""
        msg = Message()
        msg.set_payload('Just text')
        
        with patch('paper_inbox.modules.utils.get_data_download_dir') as mock_dir:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_dir.return_value = tmpdir
                
                result = download_attachments(msg, 123)
                assert result == []
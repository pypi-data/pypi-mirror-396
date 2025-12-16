# tests/test_telegram.py
"""Tests for telegram module"""
from unittest.mock import MagicMock, patch

import requests  # <-- Add this import

from paper_inbox.modules.telegram import send_msg, send_telegram_notification


class TestTelegram:
    """Test Telegram notification functions"""
    
    def test_send_telegram_notification_skips_when_disabled(self):
        """Test notification is skipped when disabled"""
        with patch('paper_inbox.modules.config.send_telegram_notifications', False):
            with patch('paper_inbox.modules.telegram.send_msg') as mock_send:
                send_telegram_notification('Test message')
                mock_send.assert_not_called()
    
    def test_send_telegram_notification_sends_when_enabled(self):
        """Test notification is sent when enabled"""
        with patch('paper_inbox.modules.config.send_telegram_notifications', True):
            with patch('paper_inbox.modules.telegram.send_msg') as mock_send:
                send_telegram_notification('Test message')
                mock_send.assert_called_once_with('Test message')
    
    def test_send_msg_success(self):
        """Test successful message sending"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'ok': True}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            with patch('paper_inbox.modules.config.telegram_bot_token', 'test-token'):
                with patch('paper_inbox.modules.config.telegram_chat_id', '123456'):
                    result = send_msg('Test message')
                    assert result == {'ok': True}
                    mock_post.assert_called_once()
    
    def test_send_msg_handles_request_exception(self):
        """Test error handling for request exceptions"""
        with patch('requests.post') as mock_post:
            # Raise a RequestException (which is what the code actually catches)
            mock_post.side_effect = requests.RequestException('Network error')
            
            with patch('paper_inbox.modules.config.telegram_bot_token', 'test-token'):
                with patch('paper_inbox.modules.config.telegram_chat_id', '123456'):
                    result = send_msg('Test message')
                    assert result is None
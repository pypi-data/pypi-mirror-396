# tests/test_utils.py
"""Tests for utils module"""
import os
import tempfile
from unittest.mock import patch

from paper_inbox.modules.utils import (
    collect_files_to_print,
    get_data_download_dir,
    is_on_home_network,
    retry_on_failure,
)


class TestUtils:
    """Test utility functions"""
    
    def test_is_on_home_network_returns_true_for_trusted_ssid(self):
        """Test network check returns True for trusted SSID"""
        with patch('subprocess.check_output') as mock_cmd:
            mock_cmd.return_value = b'HomeWifi\n'
            
            with patch('paper_inbox.modules.config.trusted_ssids', ['HomeWifi']):
                result = is_on_home_network()
                assert result is True
    
    def test_is_on_home_network_returns_false_for_untrusted_ssid(self):
        """Test network check returns False for untrusted SSID"""
        with patch('subprocess.check_output') as mock_cmd:
            mock_cmd.return_value = b'PublicWifi\n'
            
            with patch('paper_inbox.modules.config.trusted_ssids', ['HomeWifi']):
                result = is_on_home_network()
                assert result is False
    
    def test_is_on_home_network_handles_exception(self):
        """Test network check handles exception gracefully"""
        with patch('subprocess.check_output') as mock_cmd:
            mock_cmd.side_effect = FileNotFoundError()
            
            result = is_on_home_network()
            assert result is False
    
    def test_get_data_download_dir(self):
        """Test getting download directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('paper_inbox.modules.config.paths.get_data_dir') as mock_dir:
                mock_dir.return_value = tmpdir
                
                result = get_data_download_dir(123, ensure_exists=True)
                assert os.path.exists(result)
                assert '123' in result
    
    def test_collect_files_to_print(self):
        """Test collecting files to print"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            email_pdf = os.path.join(tmpdir, 'email.pdf')
            attachment = os.path.join(tmpdir, 'attachment.pdf')
            
            open(email_pdf, 'w').close()
            open(attachment, 'w').close()
            
            with patch('paper_inbox.modules.utils.get_data_download_dir') as mock_dir:
                mock_dir.return_value = tmpdir
                
                result = collect_files_to_print(123)
                # email.pdf should be first
                assert result[0].endswith('email.pdf')
                assert len(result) == 2
    
    def test_collect_files_to_print_empty_directory(self):
        """Test collecting files from empty directory"""
        with patch('paper_inbox.modules.utils.get_data_download_dir') as mock_dir:
            mock_dir.return_value = '/nonexistent/directory'
            
            result = collect_files_to_print(123)
            assert result == []
    
    def test_retry_on_failure_decorator(self):
        """Test retry decorator with successful call"""
        @retry_on_failure()
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_retry_on_failure_with_retriable_exception(self):
        """Test retry decorator with retriable exception"""
        call_count = {'count': 0}
        
        @retry_on_failure()
        def failing_function():
            call_count['count'] += 1
            if call_count['count'] < 2:
                from socket import gaierror
                raise gaierror("Network error")
            return "success"
        
        with patch('paper_inbox.modules.config.network_retry_delay', 0.1):
            result = failing_function()
            assert result == "success"
            assert call_count['count'] == 2
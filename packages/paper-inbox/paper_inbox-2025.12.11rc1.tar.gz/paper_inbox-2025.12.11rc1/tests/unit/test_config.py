# tests/test_config.py
"""Tests for configuration module"""
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

from paper_inbox.modules.config import file, validators


class TestConfigFile:
    """Test config file operations"""
    
    def test_init_config_creates_default_config(self, tmp_path):
        """Test that init_config creates a config with default values"""
        mock_file = tmp_path / "config.toml"

        with patch('paper_inbox.modules.config.file.get_config_filepath') as mock_path:
            mock_path.return_value = mock_file
            result = file.init_config()
            assert result is True
            assert mock_file.is_file()
    
    def test_get_config_returns_empty_dict_when_no_file(self):
        """Test that get_config returns empty dict when file doesn't exist"""
        with patch('paper_inbox.modules.config.file.get_config_filepath') as mock_path:
            mock_path.return_value = Path('/nonexistent/path/config.toml')
            config = file.get_config()
            assert config == {}
    
    def test_write_config_creates_new_file(self):
        """Test that write_config creates a new config file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toml') as f:
            temp_path = Path(f.name)
        
        try:
            with patch('paper_inbox.modules.config.file.get_config_filepath') as mock_path:
                mock_path.return_value = temp_path
                test_config = {"TEST_KEY": "test_value"}
                result = file.write_config(test_config, merge=False)
                assert result is True
                
                # Verify the config was written
                written_config = file.get_config()
                assert written_config["TEST_KEY"] == "test_value"
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_write_config_merges_with_existing(self):
        """Test that write_config merges with existing config when merge=True"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toml') as f:
            temp_path = Path(f.name)
        
        try:
            with patch('paper_inbox.modules.config.file.get_config_filepath') as mock_path:
                mock_path.return_value = temp_path
                
                # Write initial config
                initial_config = {"KEY1": "value1", "KEY2": "value2"}
                file.write_config(initial_config, merge=False)
                
                # Update with merge
                update_config = {"KEY2": "updated_value", "KEY3": "value3"}
                file.write_config(update_config, merge=True)
                
                # Verify merge
                final_config = file.get_config()
                assert final_config["KEY1"] == "value1"
                assert final_config["KEY2"] == "updated_value"
                assert final_config["KEY3"] == "value3"
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestConfigValidators:
    """Test config validation functions"""
    
    def test_has_email_account_defined_returns_true(self):
        """Test email account validator with valid account"""
        # Mock where get_config is USED (in validators module), not where it's defined
        with patch('paper_inbox.modules.config.validators.get_config') as mock_config:
            mock_config.return_value = {"EMAIL_ACCOUNT": "test@example.com"}
            assert validators.has_email_account_defined() is True
    
    def test_has_email_account_defined_returns_false_when_empty(self):
        """Test email account validator with empty account"""
        with patch('paper_inbox.modules.config.validators.get_config') as mock_config:
            mock_config.return_value = {"EMAIL_ACCOUNT": ""}
            assert validators.has_email_account_defined() is False
    
    def test_has_email_account_defined_returns_false_when_none(self):
        """Test email account validator with None"""
        with patch('paper_inbox.modules.config.validators.get_config') as mock_config:
            mock_config.return_value = {}
            assert validators.has_email_account_defined() is False
    
    def test_has_sender_emails_defined_returns_true(self):
        """Test sender emails validator with valid senders"""
        with patch('paper_inbox.modules.config.validators.get_config') as mock_config:
            mock_config.return_value = {"EMAIL_FROM": ["sender@example.com"]}
            assert validators.has_sender_emails_defined() is True
    
    def test_has_sender_emails_defined_returns_false_when_empty(self):
        """Test sender emails validator with empty list"""
        with patch('paper_inbox.modules.config.validators.get_config') as mock_config:
            mock_config.return_value = {"EMAIL_FROM": []}
            assert validators.has_sender_emails_defined() is False
    
    def test_has_trusted_network_defined_returns_true(self):
        """Test trusted network validator with valid SSIDs"""
        with patch('paper_inbox.modules.config.validators.get_config') as mock_config:
            mock_config.return_value = {"TRUSTED_SSIDS": ["HomeWifi"]}
            assert validators.has_trusted_network_defined() is True
    
    def test_has_trusted_network_defined_returns_false_when_empty(self):
        """Test trusted network validator with empty list"""
        with patch('paper_inbox.modules.config.validators.get_config') as mock_config:
            mock_config.return_value = {"TRUSTED_SSIDS": []}
            assert validators.has_trusted_network_defined() is False
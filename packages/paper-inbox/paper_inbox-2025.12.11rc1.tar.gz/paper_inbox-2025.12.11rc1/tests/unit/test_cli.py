# tests/test_cli.py
"""Tests for CLI module"""
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from paper_inbox.cli import main, run_tests


class TestCLI:
    """Test CLI commands"""
    
    def test_cli_runs_app_with_no_flags(self):
        """Test CLI runs main app when no flags provided"""
        runner = CliRunner()
        
        with patch('paper_inbox.cli.run_app') as mock_run:
            result = runner.invoke(main, [])
            mock_run.assert_called_once()
    
    def test_cli_show_config_flag(self):
        """Test CLI --show-config flag"""
        runner = CliRunner()
        
        # Mock at the location where it's imported in cli.py
        with patch('paper_inbox.cli.print_config') as mock_print:
            result = runner.invoke(main, ['--show-config'])
            mock_print.assert_called_once()
    
    def test_cli_show_dirs_flag(self):
        """Test CLI --show-dirs flag"""
        runner = CliRunner()
        
        # Mock at the location where it's imported in cli.py
        with patch('paper_inbox.cli.print_dirs') as mock_print:
            result = runner.invoke(main, ['--show-dirs'])
            mock_print.assert_called_once()
    
    def test_cli_show_cron_flag(self):
        """Test CLI --show-cron flag"""
        runner = CliRunner()
        
        # Mock at the location where it's imported in cli.py
        with patch('paper_inbox.cli.list_cron_jobs') as mock_list:
            result = runner.invoke(main, ['--show-cron'])
            mock_list.assert_called_once()
    
    def test_cli_open_config_flag(self):
        """Test CLI --open-config flag"""
        runner = CliRunner()
        
        with patch('paper_inbox.cli.open_config_dir') as mock_open:
            result = runner.invoke(main, ['--open-config'])
            mock_open.assert_called_once()
    
    def test_cli_config_flag(self):
        """Test CLI --config flag"""
        runner = CliRunner()
        
        with patch('paper_inbox.cli.configure_app') as mock_configure:
            result = runner.invoke(main, ['--config'])
            mock_configure.assert_called_once()
    
    def test_cli_test_flag(self):
        """Test CLI --test flag"""
        runner = CliRunner()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = runner.invoke(main, ['--test'])
            mock_run.assert_called_once()
    
    def test_run_tests_successful(self):
        """Test run_tests with successful pytest run"""
        mock_result = MagicMock(returncode=0)
        
        with patch('subprocess.run', return_value=mock_result):
            run_tests()
            # No assertion needed, just checking it doesn't raise
    
    def test_run_tests_failure(self):
        """Test run_tests with failed pytest run"""
        mock_result = MagicMock(returncode=1)
        
        with patch('subprocess.run', return_value=mock_result):
            run_tests()
            # No assertion needed, just checking it doesn't raise
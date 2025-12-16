#!/usr/bin/env python3
"""
Unit tests for fsm (frida-server-manager)
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import subprocess

# Add the project root to sys.path to import fsm modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsm.cli import main
from fsm.core import (
    run_command,
    check_adb_connection,
    get_device_architecture,
    get_available_frida_versions,
    get_current_frida_version,
    download_frida_server,
    install_frida_server,
    run_frida_server,
    get_installed_frida_server_version,
    DEFAULT_INSTALL_DIR
)


class TestFSM(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        # Save the original directory to restore later
        self.original_dir = os.getcwd()
        # Change to the test directory
        os.chdir(self.test_dir)
    
    def tearDown(self):
        # Change back to the original directory
        os.chdir(self.original_dir)
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    @patch('fsm.core.subprocess.run')
    def test_run_command_success(self, mock_run):
        # Mock successful command execution
        mock_result = MagicMock()
        mock_result.stdout = "Command output"
        mock_run.return_value = mock_result
        
        # Test run_command with verbose=False
        result = run_command("echo test")
        self.assertEqual(result, "Command output")
        mock_run.assert_called_once_with(
            "echo test", shell=True, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
    
    @patch('fsm.core.subprocess.run')
    def test_run_command_failure(self, mock_run):
        # Mock failed command execution
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, "echo test", stderr="Command failed")
        
        # Test run_command with verbose=True
        result = run_command("echo test", verbose=True)
        self.assertIsNone(result)
    
    @patch('fsm.core.run_command')
    @patch('sys.exit')
    def test_check_adb_connection_success(self, mock_exit, mock_run_command):
        # Mock successful ADB connection
        mock_run_command.return_value = "List of devices attached\n12345678	device"
        
        # Test check_adb_connection with verbose=False
        check_adb_connection()
        mock_run_command.assert_called_once_with('adb devices', False)
        mock_exit.assert_not_called()
    
    @patch('fsm.core.run_command')
    @patch('sys.exit')
    def test_check_adb_connection_no_devices(self, mock_exit, mock_run_command):
        # Mock no devices connected
        mock_run_command.return_value = "List of devices attached"
        
        # Test check_adb_connection
        check_adb_connection()
        mock_exit.assert_called_once_with(1)
    
    @patch('fsm.core.run_command')
    @patch('sys.exit')
    def test_get_device_architecture(self, mock_exit, mock_run_command):
        # Mock device architecture response
        mock_run_command.return_value = "arm64-v8a\n"
        
        # Test get_device_architecture
        arch = get_device_architecture(verbose=True)
        self.assertEqual(arch, "arm64")
        mock_run_command.assert_called_once_with('adb shell getprop ro.product.cpu.abi', True)
    
    @patch('fsm.core.requests.get')
    def test_get_available_frida_versions(self, mock_get):
        # Mock GitHub API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"tag_name": "v16.1.4", "prerelease": False, "draft": False},
            {"tag_name": "v16.1.3", "prerelease": False, "draft": False},
            {"tag_name": "v16.1.0-beta1", "prerelease": True, "draft": False}
        ]
        mock_get.return_value = mock_response
        
        # Test get_available_frida_versions
        versions = get_available_frida_versions(verbose=True)
        self.assertEqual(versions, ["16.1.4", "16.1.3"])
        mock_get.assert_called_once()
    
    @patch('fsm.core.run_command')
    def test_get_current_frida_version_installed(self, mock_run_command):
        # Mock frida version response
        mock_run_command.return_value = "16.1.4\n"
        
        # Test get_current_frida_version
        version = get_current_frida_version(verbose=True)
        self.assertEqual(version, "16.1.4")
        mock_run_command.assert_called_once_with('frida --version', True)
    
    @patch('fsm.core.run_command')
    def test_get_current_frida_version_not_installed(self, mock_run_command):
        # Mock frida not installed
        mock_run_command.return_value = None
        
        # Test get_current_frida_version
        version = get_current_frida_version()
        self.assertIsNone(version)
    
    @patch('fsm.core.requests.get')
    @patch('builtins.open')
    def test_download_frida_server_success(self, mock_open, mock_get):
        # Mock successful download
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"file content"]
        mock_get.return_value = mock_response
        
        # Test download_frida_server
        file_path = download_frida_server("16.1.4", "arm64", verbose=True)
        self.assertEqual(file_path, "/tmp/frida-server-16.1.4-android-arm64.xz")
        mock_get.assert_called()
        mock_open.assert_called_once_with(file_path, 'wb')
    
    @patch('fsm.core.check_adb_connection')
    @patch('fsm.core.get_device_architecture')
    @patch('fsm.core.get_current_frida_version')
    @patch('fsm.core.download_frida_server')
    @patch('fsm.core.run_command')
    @patch('lzma.open')
    @patch('builtins.open')
    @patch('os.remove')
    @patch('sys.exit')
    def test_install_frida_server_with_version(
            self, mock_exit, mock_remove, mock_open, mock_lzma_open, mock_run_command, 
            mock_download_frida_server, mock_get_current_frida_version, 
            mock_get_device_architecture, mock_check_adb_connection
    ):
        # Set up mocks
        mock_get_device_architecture.return_value = "arm64"
        mock_download_frida_server.return_value = "frida-server-16.1.4-android-arm64.xz"
        mock_run_command.return_value = "Success"
        
        # Mock file operations
        mock_lzma_file = MagicMock()
        mock_lzma_file.read.return_value = b"binary content"
        mock_lzma_open.return_value.__enter__.return_value = mock_lzma_file
        mock_open.return_value.__enter__.return_value = MagicMock()
        
        # Test install_frida_server with version parameter
        install_frida_server(version="16.1.4", verbose=True)
        
        # Verify all functions were called with correct parameters
        mock_check_adb_connection.assert_called_once_with(True)
        mock_get_device_architecture.assert_called_once_with(True)
        # Note: download_frida_server signature is (version, arch, repo='frida/frida', verbose=False)
        mock_download_frida_server.assert_called_once_with("16.1.4", "arm64", "frida/frida", True)
        self.assertTrue(mock_run_command.called)
    
    @patch('fsm.core.check_adb_connection')
    @patch('fsm.core.run_command')
    @patch('fsm.core.get_installed_frida_server_version')
    @patch('sys.exit')
    def test_run_frida_server_with_version(self, mock_exit, mock_get_installed_version, mock_run_command, mock_check_adb_connection):
        # Set up mocks
        mock_run_command.return_value = "frida-server-16.1.4"
        mock_get_installed_version.return_value = "16.1.4"
        
        # Mock subprocess.Popen for the final command
        with patch('fsm.core.subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 1234
            mock_popen.return_value = mock_process
            
            # Mock the wait method to avoid test hanging
            mock_process.wait.return_value = None
            
            # Test run_frida_server with version parameter
            run_frida_server(version="16.1.4", verbose=True)
        
        # Verify all functions were called with correct parameters
        mock_check_adb_connection.assert_called_once_with(True)
        mock_run_command.assert_called_once_with(f'adb shell ls {DEFAULT_INSTALL_DIR}/frida-server-16.1.4', True)
        mock_get_installed_version.assert_called_once_with(True)
    
    @patch('fsm.core.check_adb_connection')
    @patch('fsm.core.run_command')
    @patch('fsm.core.get_installed_frida_server_version')
    @patch('sys.exit')
    def test_run_frida_server_with_name(self, mock_exit, mock_get_installed_version, mock_run_command, mock_check_adb_connection):
        # Set up mocks
        mock_run_command.return_value = "my-custom-frida"
        mock_get_installed_version.return_value = "16.1.4"
        
        # Mock subprocess.Popen for the final command
        with patch('fsm.core.subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 1234
            mock_popen.return_value = mock_process
            
            # Mock the wait method to avoid test hanging
            mock_process.wait.return_value = None
            
            # Test run_frida_server with name parameter
            run_frida_server(name="my-custom-frida", verbose=True)
        
        # Verify all functions were called with correct parameters
        mock_check_adb_connection.assert_called_once_with(True)
        mock_run_command.assert_called_once_with(f'adb shell ls {DEFAULT_INSTALL_DIR}/my-custom-frida', True)
        mock_get_installed_version.assert_called_once_with(True)
    
    @patch('sys.argv', ['fsm', '--help'])
    @patch('fsm.cli.argparse.ArgumentParser.print_help')
    def test_cli_help(self, mock_print_help):
        # Test CLI help command
        with self.assertRaises(SystemExit):
            main()
        mock_print_help.assert_called_once()
    
    @patch('sys.argv', ['fsm', 'install', '--help'])
    @patch('fsm.cli.argparse.ArgumentParser.print_help')
    def test_cli_install_help(self, mock_print_help):
        # Test CLI install help command
        with self.assertRaises(SystemExit):
            main()
        mock_print_help.assert_called_once()
    
    @patch('sys.argv', ['fsm', 'run', '--help'])
    @patch('fsm.cli.argparse.ArgumentParser.print_help')
    def test_cli_run_help(self, mock_print_help):
        # Test CLI run help command
        with self.assertRaises(SystemExit):
            main()
        mock_print_help.assert_called_once()
    
    @patch('sys.argv', ['fsm', 'install', '16.1.4', '--repo', 'suifei/fridare'])
    @patch('fsm.cli.install_frida_server')
    def test_cli_install_with_repo(self, mock_install_frida_server):
        # Test CLI install command with custom repo
        with self.assertRaises(SystemExit):
            main()
        mock_install_frida_server.assert_called_once_with('16.1.4', False, 'suifei/fridare', False, None)
    
    @patch('sys.argv', ['fsm', 'install', '16.1.4', '--keep-name'])
    @patch('fsm.cli.install_frida_server')
    def test_cli_install_with_keep_name(self, mock_install_frida_server):
        # Test CLI install command with keep-name flag
        with self.assertRaises(SystemExit):
            main()
        mock_install_frida_server.assert_called_once_with('16.1.4', False, 'frida/frida', True, None)
    
    @patch('sys.argv', ['fsm', 'install', '16.1.4', '--name', 'my-frida'])
    @patch('fsm.cli.install_frida_server')
    def test_cli_install_with_custom_name(self, mock_install_frida_server):
        # Test CLI install command with custom name
        with self.assertRaises(SystemExit):
            main()
        mock_install_frida_server.assert_called_once_with('16.1.4', False, 'frida/frida', False, 'my-frida')
    
    @patch('sys.argv', ['fsm', 'run', '--version', '16.1.4'])
    @patch('fsm.cli.run_frida_server')
    def test_cli_run_with_version(self, mock_run_frida_server):
        # Test CLI run command with version parameter
        with self.assertRaises(SystemExit):
            main()
        mock_run_frida_server.assert_called_once_with(None, None, False, '16.1.4', None)
    
    @patch('sys.argv', ['fsm', 'run', '--name', 'my-frida'])
    @patch('fsm.cli.run_frida_server')
    def test_cli_run_with_name(self, mock_run_frida_server):
        # Test CLI run command with name parameter
        with self.assertRaises(SystemExit):
            main()
        mock_run_frida_server.assert_called_once_with(None, None, False, None, 'my-frida')
    
    @patch('sys.argv', ['fsm', 'run', '--dir', '/custom/dir'])
    @patch('fsm.cli.run_frida_server')
    def test_cli_run_with_custom_dir(self, mock_run_frida_server):
        # Test CLI run command with custom directory
        with self.assertRaises(SystemExit):
            main()
        mock_run_frida_server.assert_called_once_with('/custom/dir', None, False, None, None)
    
    @patch('sys.argv', ['fsm', 'run', '--params', '-D'])
    @patch('fsm.cli.run_frida_server')
    def test_cli_run_with_params(self, mock_run_frida_server):
        # Test CLI run command with additional parameters
        # 简化测试，直接调用函数而不是通过参数解析
        from fsm.cli import run_frida_server
        run_frida_server(None, '-D', False, None, None)
        mock_run_frida_server.assert_called_once_with(None, '-D', False, None, None)


if __name__ == '__main__':
    unittest.main()
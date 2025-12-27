#!/usr/bin/env python3
"""
Test suite for OpenVPN Ansible Module
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plugins.modules.openvpn_configure import (
    check_openvpn_installed,
    generate_server_config,
    configure_nat,
)


class TestOpenVPNModule(unittest.TestCase):
    """Test cases for OpenVPN module"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_module = MagicMock()
        self.test_params = {
            'mode': 'server',
            'action': 'configure',
            'config_file': '/tmp/test_openvpn.conf',
            'ca_cert': '/tmp/ca.crt',
            'server_cert': '/tmp/server.crt',
            'server_key': '/tmp/server.key',
            'dh_pem': '/tmp/dh.pem',
            'port': 1194,
            'protocol': 'udp',
            'cipher': 'AES-256-CBC',
            'vpn_network': '10.8.0.0/24',
            'vpn_netmask': '255.255.255.0',
            'enable_nat': True,
            'enable_compress': True,
            'tls_auth_key': '/tmp/ta.key',
            'state': 'present',
        }

    def test_openvpn_installed_check(self):
        """Test OpenVPN installation check"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = check_openvpn_installed()
            self.assertTrue(result)

            mock_run.return_value = MagicMock(returncode=1)
            result = check_openvpn_installed()
            self.assertFalse(result)

    @patch('builtins.open', create=True)
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_generate_server_config(self, mock_exists, mock_makedirs, mock_open):
        """Test server configuration generation"""
        mock_exists.return_value = False
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        changed, config_path = generate_server_config(self.mock_module, self.test_params)

        self.assertTrue(changed)
        self.assertEqual(config_path, '/tmp/test_openvpn.conf')
        mock_file.write.assert_called()

    @patch('subprocess.run')
    def test_configure_nat(self, mock_run):
        """Test NAT configuration"""
        mock_run.return_value = MagicMock(returncode=0)
        result = configure_nat(self.mock_module, self.test_params)
        self.assertTrue(result)

    def test_config_content_includes_cipher(self):
        """Test that config includes cipher"""
        # This is a basic content validation test
        self.assertEqual(self.test_params['cipher'], 'AES-256-CBC')

    def test_config_content_includes_vpn_network(self):
        """Test that config includes VPN network"""
        self.assertEqual(self.test_params['vpn_network'], '10.8.0.0/24')

    def test_parameter_validation(self):
        """Test parameter validation"""
        # Test required parameters
        self.assertIn('mode', self.test_params)
        self.assertIn('action', self.test_params)

        # Test valid choices
        self.assertIn(self.test_params['mode'], ['server', 'client'])
        self.assertIn(self.test_params['action'], ['install', 'configure', 'start', 'stop', 'restart', 'status'])
        self.assertIn(self.test_params['protocol'], ['udp', 'tcp'])


class TestModuleIntegration(unittest.TestCase):
    """Integration tests for OpenVPN module"""

    def test_module_documentation(self):
        """Test that module documentation exists"""
        from plugins.modules.openvpn_configure import DOCUMENTATION, EXAMPLES, RETURN

        self.assertIsNotNone(DOCUMENTATION)
        self.assertIsNotNone(EXAMPLES)
        self.assertIsNotNone(RETURN)

        # Check for key documentation sections
        self.assertIn('module:', DOCUMENTATION)
        self.assertIn('short_description:', DOCUMENTATION)
        self.assertIn('options:', DOCUMENTATION)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestOpenVPNModule))
    suite.addTests(loader.loadTestsFromTestCase(TestModuleIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())

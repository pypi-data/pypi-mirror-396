#!/usr/bin/env python

"""
Purpose: tests
"""
import socket
import unittest
from unittest.mock import patch

from pkg_19544.helpers.evaluate import _is_fqdn_ipaddr_public_routable


class TestEvaluateUrlIps(unittest.TestCase):
    def test_is_fqdn_ipaddr_public_routable_true(self):
        fqdn = "example.com"
        self.assertTrue(_is_fqdn_ipaddr_public_routable('https', fqdn))

    def test_is_fqdn_ipaddr_public_routable_false_gaierror(self):
        fqdn = "example.com"
        with patch('socket.getaddrinfo') as mock_getaddrinfo:
            mock_getaddrinfo.side_effect = socket.gaierror("Unknown host")
            with self.assertRaises(ValueError):
                return _is_fqdn_ipaddr_public_routable('https', fqdn)

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_public_routable_false_invalid_ips(self, mock_getaddrinfo):
        fqdn = "example.com"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))
        ]
        with self.assertRaises(ValueError):
            return _is_fqdn_ipaddr_public_routable('https', fqdn)

#!/usr/bin/env python

"""
Purpose: tests
"""
import unittest
from unittest.mock import MagicMock, patch

from pkg_19544.helpers.evaluate import _has_valid_tls


class TestEvaluateUrlTls(unittest.TestCase):
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_true(self, mock_wrap_socket, mock_create_connection):
        fqdn = "example.com"
        netloc = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': 'Nov 12 12:12:12 2025 GMT',
            'notAfter': 'Feb 12 12:12:12 2046 GMT',
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict
        self.assertTrue(_has_valid_tls(netloc, fqdn))

    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_false_invalid_cipher(self, mock_wrap_socket, mock_create_connection):
        fqdn = "example.com"
        netloc = "example.com"

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ''

        with self.assertRaises(ValueError):
            return _has_valid_tls(netloc, fqdn)

    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_false_weak_cipher(self, mock_wrap_socket, mock_create_connection):
        fqdn = "example.com"
        netloc = "example.com"

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_NULL_SHA256', 'TLSv1.3', '256')

        with self.assertRaises(ValueError):
            return _has_valid_tls(netloc, fqdn)

    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_false_weak_hashing(self, mock_wrap_socket, mock_create_connection):
        fqdn = "example.com"
        netloc = "example.com"

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA1', 'TLSv1.3', '256')

        with self.assertRaises(ValueError):
            return _has_valid_tls(netloc, fqdn)

    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_false_weak_protocol(self, mock_wrap_socket, mock_create_connection):
        fqdn = "example.com"
        netloc = "example.com"

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_128_GCM_SHA256', 'TLSv1.2', '128')

        with self.assertRaises(ValueError):
            return _has_valid_tls(netloc, fqdn)

    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_false_cert_not_dict(self, mock_wrap_socket, mock_create_connection):
        fqdn = "example.com"
        netloc = "example.com"
        cert_dict = []

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict

        with self.assertRaises(ValueError):
            return _has_valid_tls(netloc, fqdn)

    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_false_cert_invalid_content(self, mock_wrap_socket, mock_create_connection):
        fqdn = "example.com"
        netloc = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': 'Nov 12 12:12:12 2025 GMT',
            'notAfter': {},
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict

        with self.assertRaises(ValueError):
            return _has_valid_tls(netloc, fqdn)

    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_false_cert_expired(self, mock_wrap_socket, mock_create_connection):
        fqdn = "example.com"
        netloc = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': 'Nov 12 12:12:12 2025 GMT',
            'notAfter': 'Feb 12 12:12:12 2016 GMT',
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict

        with self.assertRaises(ValueError):
            return _has_valid_tls(netloc, fqdn)

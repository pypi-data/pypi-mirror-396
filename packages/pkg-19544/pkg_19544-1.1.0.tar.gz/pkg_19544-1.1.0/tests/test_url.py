#!/usr/bin/env python

"""
Purpose: tests
"""
import unittest

from pkg_19544.helpers.evaluate import (
    _has_allowed_scheme,
    _has_no_basic_auth,
    _has_no_control_character,
    _has_valid_fqdn_label,
    _has_valid_fqdn_syntax,
    _has_valid_tld,
    _is_fqdn_resolvable,
)
from pkg_19544.helpers.sanitize import _encode_url_components, _remove_control_characters


class TestEvaluateUrl(unittest.TestCase):
    def test_has_allowed_scheme_true(self):
        user_url = "https://example.com/path1/path2?key=value#section1.1"
        self.assertTrue(_has_allowed_scheme(user_url))

    def test_has_allowed_scheme_false(self):
        user_url = "http://example.com/path1/path2?key=value#section1.1"
        with self.assertRaises(ValueError):
            return _has_allowed_scheme(user_url)

    def test_has_no_basic_auth_true(self):
        userinfo = ""
        self.assertTrue(_has_no_basic_auth(userinfo))

    def test_has_no_basic_auth_false(self):
        userinfo = "user:pass"
        with self.assertRaises(ValueError):
            return _has_no_basic_auth(userinfo)

    def test_has_no_control_character_true(self):
        user_url = "https://example.com/path1/path2?key=value#section1.1"
        self.assertTrue(_has_no_control_character(user_url))

    def test_has_no_control_character_false(self):
        user_url = "http://example.com/pa\nth1/path2?key=va\rlue#section1.1"
        with self.assertRaises(ValueError):
            return _has_no_control_character(user_url)

    def test_has_valid_fqdn_syntax_true(self):
        fqdn = "example.com"
        self.assertTrue(_has_valid_fqdn_syntax(fqdn))

    def test_has_valid_fqdn_syntax_false_no_dot(self):
        fqdn = "examplecom"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    def test_has_valid_fqdn_syntax_false_chars(self):
        fqdn = "examp:lecom"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    def test_has_valid_fqdn_syntax_false_length(self):
        fqdn = "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "example.com"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    def test_has_valid_fqdn_label_true(self):
        fqdn = "12345678901234567890123456789012345678901234567890.example.com"
        self.assertTrue(_has_valid_fqdn_label(fqdn))

    def test_has_valid_fqdn_label_false_hyphen_prefix(self):
        fqdn = "-host.example.com"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_label(fqdn)

    def test_has_valid_fqdn_label_false_hyphen_suffix(self):
        fqdn = "host-.example.com"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_label(fqdn)

    def test_has_valid_fqdn_label_false_length(self):
        fqdn = "12345678901234567890123456789012345678901234567890" \
               "123456789012345678901234.example.com"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_label(fqdn)

    def test_has_valid_tld_true(self):
        fqdn = "host.example.com"
        self.assertTrue(_has_valid_tld(fqdn))

    def test_has_valid_tld_false_invalid_tld(self):
        fqdn = "host.example.x0m"
        with self.assertRaises(ValueError):
            return _has_valid_tld(fqdn)

    def test_is_fqdn_resolvable_true(self):
        fqdn = "example.com"
        self.assertTrue(_is_fqdn_resolvable('https', fqdn))

    def test_is_fqdn_resolvable_false(self):
        fqdn = "invalid.host.example.site"
        with self.assertRaises(ValueError):
            return _is_fqdn_resolvable('https', fqdn)


class TestSanitizeUrl(unittest.TestCase):
    def test_remove_control_characters_true_control_chars_no(self):
        user_url = "https://example.com/search+test?key1=value1#section-3.11"

        updated_url = _remove_control_characters(user_url)
        assert updated_url is not None

    def test_remove_control_characters_true_control_chars_yes(self):
        user_url = "https://example.com/search+te\rst?key1=val\r\nue1#section-3.11 "
        user_url_length = len(user_url)

        updated_url = _remove_control_characters(user_url)
        updated_url_length = len(updated_url)

        diff = user_url_length - updated_url_length

        assert updated_url is not None
        assert diff == 4
        assert updated_url == "https://example.com/search+test?key1=value1#section-3.11"

    def test_encode_url_components_true(self):
        pre_parsed_path = "/search+test?key1=value1&key2='value2'#section-3.11"

        updated_url = _encode_url_components(pre_parsed_path)
        assert "/" in updated_url[0]
        assert "+" in updated_url[0]
        assert "&" in updated_url[1]
        assert "=" in updated_url[1]
        assert "%27" in updated_url[1]
        assert "?" not in updated_url[1]
        assert "#" not in updated_url[2]

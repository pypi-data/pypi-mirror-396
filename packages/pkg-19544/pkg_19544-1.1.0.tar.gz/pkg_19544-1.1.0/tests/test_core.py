#!/usr/bin/env python

"""
Purpose: tests
"""
import unittest

from pkg_19544.core import evaluate_url, sanitize_url


class TestCore(unittest.TestCase):
    def test_evaluate_url_true(self):
        user_url = "https://example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertTrue(evaluate_url(user_url))

    def test_evaluate_url_false_bad_scheme(self):
        user_url = "http://example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_false_basic_auth(self):
        user_url = "https://user:pass@example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_false_control_char(self):
        user_url = "https://example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1Nm\r\nowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_false_fqdn_char(self):
        user_url = "https://exa_mple.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_false_fqdn_label_prefix(self):
        user_url = "https://-host.example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_false_fqdn_label_suffix(self):
        user_url = "https://host-.example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_false_tld(self):
        user_url = "https://example.tld8/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_sanitize_url_true(self):
        user_url = "https://example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertTrue(sanitize_url(user_url))

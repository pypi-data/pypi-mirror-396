# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase, skip

import mock
from commonconf import override_settings
from restclients_core.exceptions import DataFailureException
from restclients_core.models import MockHTTP

from uw_sps_contacts.dao import Contacts_Auth_DAO, Contacts_DAO
from uw_sps_contacts.utils import (
    fdao_sps_contacts_auth_override,
    fdao_sps_contacts_override,
)


@fdao_sps_contacts_auth_override
@fdao_sps_contacts_override
class TestSpsAuth(TestCase):
    """Tests for SPS Contacts Auth DAO
    """

    def test_is_cacheable(self):
        auth = Contacts_Auth_DAO()
        self.assertTrue(auth._is_cacheable("POST", "/", {}, ""))

    def test_get_auth_token(self):
        self.assertIsNotNone(
            Contacts_Auth_DAO().get_auth_token())

    @mock.patch.object(Contacts_Auth_DAO, "postURL")
    def test_get_auth_token_error(self, mock):
        response = MockHTTP()
        response.status = 404
        response.data = "Not Found"
        mock.return_value = response
        self.assertRaises(
            DataFailureException,
            Contacts_Auth_DAO().get_auth_token)

    @override_settings(RESTCLIENTS_SPS_CONTACTS_AUTH_SECRET="test1")
    @mock.patch.object(Contacts_Auth_DAO, "get_auth_token")
    def test_auth_header(self, mock_get_auth_token):
        mock_get_auth_token.return_value = "abcdef"
        headers = Contacts_DAO()._custom_headers("GET", "/", {}, "")
        self.assertTrue("Authorization" in headers)

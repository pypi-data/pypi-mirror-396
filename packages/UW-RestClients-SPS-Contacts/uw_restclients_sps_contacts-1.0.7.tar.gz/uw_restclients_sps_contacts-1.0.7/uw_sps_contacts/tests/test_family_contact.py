# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from unittest import TestCase

import mock
from restclients_core.exceptions import DataFailureException
from restclients_core.models import MockHTTP

from uw_sps_contacts import FamilyContacts
from uw_sps_contacts.models import FamilyContact


class FamilyContactsTest(TestCase):
    """Unit tests for FamilyContacts class
    """

    def test_family_contact_url(self):
        """Test that the family contact URL is correct
        """
        contact = FamilyContacts()
        self.assertEqual(
            "/student/registration/v1/address/12345",
            contact._get_contact_url(12345),
        )

    @mock.patch.object(FamilyContacts, "_get_resource")
    def test_error_401(self, mock):
        """Test that a 401 error raises DataFailureException
        """
        response = MockHTTP()
        response.status = 401
        response.data = "Not Authorized"
        mock.return_value = response
        with self.assertRaises(DataFailureException):
            FamilyContacts().get_contact(12345)

    def test_family_contact_javerage(self):
        """Test that a known family contact is returned correctly
        """
        fcontacts = FamilyContacts()
        contact = fcontacts.get_contact(12345)

        self.assertEqual('NAME,PARENT', contact.name)
        self.assertEqual('C/O STUDENT TEAM', contact.address_line_1)
        self.assertEqual('UW TOWER O-3 BOX 359565', contact.address_line_2)
        self.assertEqual('SEATTLE', contact.city)
        self.assertEqual('WA', contact.state)
        self.assertEqual('98195', contact.zip_5)
        self.assertEqual('', contact.zip_filler_b)
        self.assertEqual('2064444444', contact.phone_number)
        self.assertEqual('', contact.country)
        self.assertEqual('', contact.postal_cd)

        resp = fcontacts._get_resource(12345, clear_cached_token=True)
        self.assertIsNotNone(resp)

    def test_json_data(self):
        """Test that json_data method returns correct dictionary
        """
        contact = FamilyContact()
        contact.name = "Jake Doe"
        contact.address_line_1 = "C/O STUDENT TEAM"
        contact.address_line_2 = "UW TOWER O-3 BOX 359565"
        contact.city = "SEATTLE"
        contact.state = "WA"
        contact.zip_5 = "98195"
        contact.zip_filler_b = ""
        contact.phone_number = "5555551234"
        contact.country = ""
        contact.postal_cd = ""

        self.assertIsInstance(contact.json_data(), dict)
        string_data = (
            '{"name": "Jake Doe", '
            '"address_line_1": "C/O STUDENT TEAM", '
            '"address_line_2": "UW TOWER O-3 BOX 359565", '
            '"city": "SEATTLE", '
            '"state": "WA", '
            '"zip_5": "98195", '
            '"zip_filler_b": "", '
            '"phone_number": "5555551234", '
            '"country": "", '
            '"postal_cd": ""}'
        )
        self.assertEqual(contact.json_data(), json.loads(string_data))

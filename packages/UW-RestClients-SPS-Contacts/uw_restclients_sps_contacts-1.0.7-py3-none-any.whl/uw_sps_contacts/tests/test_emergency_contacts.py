# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import datetime
import json
from unittest import TestCase

import mock
from restclients_core.exceptions import DataFailureException
from restclients_core.models import MockHTTP

from uw_sps_contacts import EmergencyContacts
from uw_sps_contacts.models import EmergencyContact


class EmergencyContactsTest(TestCase):
    """Tests for the EmergencyContacts class.
    """

    def test_emergency_contacts_url(self):
        """Test the emergency contacts URL construction.
        """
        contacts = EmergencyContacts()
        self.assertEqual(
            "/contacts/v1/emergencyContacts/12345",
            contacts._get_contacts_url(12345),
        )

    @mock.patch.object(EmergencyContacts, "_get_resource")
    def test_error_401(self, mock):
        """Test handling of 401 Unauthorized error.
        """
        response = MockHTTP()
        response.status = 401
        response.data = "Not Authorized"
        mock.return_value = response
        with self.assertRaises(DataFailureException):
            EmergencyContacts().get_contacts(12345)

    def test_contacts_for_javerage(self):
        """Test retrieval and parsing of emergency contacts for a sample user.
        """
        contactslist = EmergencyContacts()
        contacts = contactslist.get_contacts(12345)
        self.assertEqual(len(contacts), 2)

        self.assertIsInstance(contacts, list)

        self.assertEqual(
            "ab269f37-2807-4b10-b9d3-b5f7c602d45f", contacts[0].id
        )
        self.assertEqual(12345, contacts[0].syskey)
        self.assertEqual("John Doe", contacts[0].name)
        self.assertEqual("+15551234567", contacts[0].phone_number)
        self.assertEqual("foo@example.com", contacts[0].email)
        self.assertEqual("PARENT", contacts[0].relationship)
        self.assertEqual(
            datetime.datetime(2025, 11, 11, 21, 28, 40, 180882),
            contacts[0].last_modified,
        )

        self.assertEqual(
            "eacccecd-8db7-48b7-8b0b-ff5d87e379f5", contacts[1].id
        )
        self.assertEqual(12345, contacts[1].syskey)
        self.assertEqual("Jane Doe", contacts[1].name)
        self.assertEqual("+15557654321", contacts[1].phone_number)
        self.assertEqual("bar@example.com", contacts[1].email)
        self.assertEqual("PARENT", contacts[1].relationship)
        self.assertEqual(
            datetime.datetime(2025, 11, 11, 21, 28, 40, 267776),
            contacts[1].last_modified,
        )

        resp = contactslist._get_resource(12345, clear_cached_token=True)
        self.assertIsNotNone(resp)

    def test_json_data(self):
        """Test the json_data method of EmergencyContact.
        """
        contact = EmergencyContact()
        contact.id = "totally-fake-id-1"
        contact.syskey = 0
        contact.name = "Jeremiah Doe"
        contact.phone_number = "+442079460000"
        contact.email = "oof@example.com"
        contact.relationship = "SIBLING"

        self.assertIsInstance(contact.json_data(), dict)
        string_data = (
            '{"id": "totally-fake-id-1", '
            '"syskey": 0, '
            '"name": "Jeremiah Doe", '
            '"phone_number": "+442079460000", '
            '"email": "oof@example.com", '
            '"relationship": "SIBLING", '
            '"last_modified": null}'
        )
        self.assertEqual(contact.json_data(), json.loads(string_data))

    @mock.patch.object(EmergencyContacts, "_put_resource")
    def test_update_contacts(self, mock_update):
        """Test updating emergency contacts for a user.
        """
        response = MockHTTP()
        response.status = 200
        mock_update.return_value = response
        eclist = []
        string_data = (
            '{"id": "totally-fake-id-2", '
            '"syskey": 12345, '
            '"name": "Jupiter Doe", '
            '"phoneNumber": "+442079460000", '
            '"email": "oof@example.com", '
            '"relationship": "SIBLING", '
            '"lastModified": null}'
        )
        ec1 = EmergencyContact(data=json.loads(string_data))
        ec2 = EmergencyContact()
        eclist.append(ec1)
        eclist.append(ec2)
        contactslist = EmergencyContacts()
        contactslist.put_contacts(12345, eclist)

        mock_update.assert_called_with(
            "/contacts/v1/emergencyContacts/12345",
            json.dumps(contactslist.put_list(eclist)),
        )

    def test_empty_contact(self):
        """Test the is_empty method of EmergencyContact.
        """
        string_data = (
            '{"id": "totally-fake-id-2", '
            '"syskey": 12345, '
            '"name": "Jupiter Doe", '
            '"phoneNumber": "+442079460000", '
            '"email": "oof@example.com", '
            '"relationship": "SIBLING", '
            '"lastModified": null}'
        )
        ec1 = EmergencyContact(data=json.loads(string_data))
        self.assertFalse(ec1.is_empty())
        ec2 = EmergencyContact()
        self.assertTrue(ec2.is_empty())

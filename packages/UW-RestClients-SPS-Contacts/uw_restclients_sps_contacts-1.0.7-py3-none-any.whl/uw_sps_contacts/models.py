# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import datetime

from restclients_core import models


class EmergencyContact(models.Model):
    """Model for Emergency Contact information
    """
    id = models.CharField(max_length=255)
    syskey = models.CharField(max_length=9)
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email = models.CharField(max_length=60)
    relationship = models.CharField()
    last_modified = models.DateTimeField(null=True)

    def __init__(self, *args, **kwargs):
        """Initialize EmergencyContact from data dictionary
        """
        data = kwargs.get("data")
        if data is None:
            return super().__init__(*args, **kwargs)

        self.id = data["id"]
        self.syskey = data["syskey"]
        self.name = data["name"]
        self.phone_number = data["phoneNumber"]  # camelCase from API
        self.email = data["email"]
        self.relationship = data["relationship"]
        try:
            self.last_modified = datetime.datetime.utcfromtimestamp(
                data["lastModified"]  # camelCase from API
            )
        except Exception:
            self.last_modified = None

    def is_empty(self):
        empty = (
            self.name == ""
            and self.phone_number == ""
            and self.email == ""
            and self.relationship == ""
        )
        return empty

    def json_data(self):
        """Return EmergencyContact data as dictionary
        """
        return {
            "id": self.id,
            "syskey": self.syskey,
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "relationship": self.relationship,
            "last_modified": (
                self.last_modified.isoformat()
                if (self.last_modified is not None)
                else None
            ),
        }

    def put_data(self):
        """Return EmergencyContact data for PUT request
        """
        return {
            "syskey": self.syskey,
            "name": self.name,
            "phoneNumber": self.phone_number,  # camelCase to API
            "email": self.email,
            "relationship": self.relationship,
        }


class FamilyContact(models.Model):
    """Model for Family Contact information
    """
    name = models.CharField(max_length=150)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_5 = models.CharField(max_length=10)
    zip_filler_b = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    postal_cd = models.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        """Initialize FamilyContact from data dictionary
        """
        data = kwargs.get("data")
        if data is None:
            return super().__init__(*args, **kwargs)

        self.name = kwargs["data"]["parent_name"]
        self.address_line_1 = kwargs["data"]["parent_address"]["line_1"]
        self.address_line_2 = kwargs["data"]["parent_address"]["line_2"]
        self.city = kwargs["data"]["parent_address"]["city"]
        self.state = kwargs["data"]["parent_address"]["state"]
        self.zip_5 = kwargs["data"]["parent_address"]["zip_5"]
        self.zip_filler_b = kwargs["data"]["parent_address"]["zip_filler_b"]
        self.phone_number = (
            kwargs["data"]["parent_address"]["phone_area"]
            + kwargs["data"]["parent_address"]["phone_prefix"]
            + kwargs["data"]["parent_address"]["phone_suffix"]
        )
        self.country = kwargs["data"]["parent_address"]["country"]
        self.postal_cd = kwargs["data"]["parent_address"]["postal_cd"]

    def json_data(self):
        """Return FamilyContact data as dictionary
        """
        return {
            "name": self.name,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "state": self.state,
            "zip_5": self.zip_5,
            "zip_filler_b": self.zip_filler_b,
            "phone_number": self.phone_number,
            "country": self.country,
            "postal_cd": self.postal_cd,
        }

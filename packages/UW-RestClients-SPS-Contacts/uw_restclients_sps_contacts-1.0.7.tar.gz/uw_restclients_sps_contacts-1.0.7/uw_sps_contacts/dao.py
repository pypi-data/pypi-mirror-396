# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
from os.path import abspath, dirname

from restclients_core.dao import DAO
from restclients_core.exceptions import DataFailureException

logger = logging.getLogger(__name__)


class Contacts_Auth_DAO(DAO):
    """ DAO for SPS Contacts OAuth2 Authentication
    """
    sps_contacts_access_token_url = "/oauth2/token"

    def service_name(self):
        """ Returns the service name for SPS Contacts Auth
        """
        return "sps_contacts_auth"

    def _is_cacheable(self, method, url, headers, body=None):
        return True

    def _custom_headers(self, method, url, headers, body):
        """ Add custom headers for SPS Contacts Auth requests
        """
        if not headers:
            headers = {}

        secret = self.get_service_setting("SECRET")

        headers["Authorization"] = f"Basic {secret}"
        headers["Content-type"] = "application/x-www-form-urlencoded"

        return headers

    def clear_token_from_cache(self):
        self.clear_cached_response(self.sps_contacts_access_token_url)

    def get_auth_token(self):
        """ Get an OAuth2 access token from SPS Contacts Auth
        """
        response = self.postURL(
            self.sps_contacts_access_token_url,
            body="grant_type=client_credentials",
        )

        if response.status == 200:
            data = json.loads(response.data)
            return data.get("access_token", "")

        # Something bad happened
        logger.error({
            "url": self.sps_contacts_access_token_url,
            "status": response.status,
            "data": response.data,
        })

        raise DataFailureException(
            self.sps_contacts_access_token_url, response.status, response.data)

    def service_mock_paths(self):
        """ Returns the mock resource paths for SPS Contacts Auth
        """
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path

    def _edit_mock_response(self, method, url, headers, body, response):
        if response.status == 404 and method != "GET":
            alternative_url = f"{url}.{method}"
            backend = self.get_implementation()
            new_resp = backend.load(method, alternative_url, headers, body)
            response.status = new_resp.status
            response.data = new_resp.data
            logger.debug({
                "url": alternative_url,
                "status": response.status,
                "data": response.data,
            })


class Contacts_DAO(DAO):
    """ DAO for SPS Contacts API requests
    """
    def __init__(self):
        self.auth_dao = Contacts_Auth_DAO()
        return super().__init__()

    def service_name(self):
        """ Returns the service name for SPS Contacts API
        """
        return "sps_contacts"

    def service_mock_paths(self):
        """ Returns the mock resource paths for SPS Contacts API
        """
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path

    def _custom_headers(self, method, url, headers, body):
        """ Add custom headers for SPS Contacts API requests
        """
        if not headers:
            headers = {}

        token = self.auth_dao.get_auth_token()

        headers["Authorization"] = f"Bearer {token}"
        return headers

    def clear_access_token(self):
        self.auth_dao.clear_token_from_cache()

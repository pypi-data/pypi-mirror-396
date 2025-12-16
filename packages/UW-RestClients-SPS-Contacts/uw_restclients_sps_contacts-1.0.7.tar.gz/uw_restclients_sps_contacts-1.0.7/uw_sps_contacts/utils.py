# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from commonconf import override_settings

fdao_sps_contacts_override = override_settings(
    RESTCLIENTS_SPS_CONTACTS_DAO_CLASS='Mock')
fdao_sps_contacts_auth_override = override_settings(
    RESTCLIENTS_SPS_CONTACTS_AUTH_DAO_CLASS='Mock')

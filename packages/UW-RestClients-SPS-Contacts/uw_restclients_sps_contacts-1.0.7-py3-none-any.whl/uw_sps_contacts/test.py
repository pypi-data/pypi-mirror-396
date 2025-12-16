# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from os.path import abspath, dirname

# This is just a test runner for coverage
from commonconf.backends import use_configparser_backend

if __name__ == '__main__':
    path = abspath(os.path.join(dirname(__file__),
                                "..", "conf", "test.conf"))
    use_configparser_backend(path, 'SPS_CONTACTS')

    from nose2 import discover
    discover()

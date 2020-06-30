# -*- coding: utf-8 -*-
# Copyright (C) 2006-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Unit and functional test suite for vigirrd."""

import platform
import os.path
import unittest

from paste.deploy import loadapp
from webtest import TestApp
from gearbox.main import GearBox

from vigirrd.model import metadata, DBSession

__all__ = ['TestController']

class TestController(unittest.TestCase):
    application_under_test = 'main_without_authn'

    def setUp(self):
        """Method called by nose before running each test"""
        # Loading the application:
        conf_dir = "."

        # Charge "test32.ini" pour les archis 32 bits
        # et "test64.ini" pour les archis 64 bits.
        arch = (platform.machine() != 'i686') and '64' or '32'
        config_file = os.path.join(conf_dir, 'test%s.ini' % arch)
        wsgiapp = loadapp('config:%s#%s' % (config_file,
                                            self.application_under_test),
                          relative_to=conf_dir)
        self.app = TestApp(wsgiapp)
        box = GearBox()
        box.run(['setup-app', '-q', '--debug', '-c', config_file])

# -*- coding: utf-8 -*-
# Copyright (C) 2006-2014 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Unit and functional test suite for vigirrd."""

import os
import sys
import platform

import unittest
from tg import config
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from webtest import TestApp
from nose.tools import eq_

from vigirrd.model import metadata, DBSession

__all__ = ['setup_db', 'teardown_db', 'TestController']

#def setup_db():
#    """Method used to build a database"""
#    print "Creating model"
#    engine = config['pylons.app_globals'].sa_engine
#    metadata.create_all(engine)
#
#def teardown_db():
#    """Method used to destroy a database"""
#    print "Destroying model"
#    engine = config['pylons.app_globals'].sa_engine
#    metadata.drop_all(engine)

class TestController(unittest.TestCase):
    """
    Base functional test case for the controllers.

    The vigirrd application instance (``self.app``) set up in this test
    case (and descendants) has authentication disabled, so that developers can
    test the protected areas independently of the :mod:`repoze.who` plugins
    used initially. This way, authentication can be tested once and separately.

    Check vigirrd.tests.functional.test_authentication for the repoze.who
    integration tests.

    This is the officially supported way to test protected areas with
    repoze.who-testutil (http://code.gustavonarea.net/repoze.who-testutil/).

    """

    application_under_test = 'main_without_authn'

    def setUp(self):
        """Method called by nose before running each test"""
        # Loading the application:
        conf_dir = config.here

        # Charge "test32.ini" pour les archis 32 bits
        # et "test64.ini" pour les archis 64 bits.
        arch = (platform.machine() != 'i686') and '64' or '32'
        config_file = os.path.join(conf_dir, 'test%s.ini' % arch)
        wsgiapp = loadapp('config:%s#%s' % (config_file,
                                            self.application_under_test),
                          relative_to=conf_dir)
        self.app = TestApp(wsgiapp)
        ## Setting it up:
        #cmd = SetupCommand('setup-app')
        #cmd.run([config_file])

    #def tearDown(self):
    #    """Method called by nose after running each test"""
    #    engine = config['pylons.app_globals'].sa_engine
    #    metadata.drop_all(engine)

# -*- coding: utf-8 -*-
# pylint: disable-msg=C0111,R0904
# Copyright (C) 2006-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import time

from vigirrd.lib import conffile
from vigirrd.tests import TestController

class TestMisc(TestController):
    def setUp(self):
        super(TestMisc, self).setUp()
        conffile.reload()
        self.now = int(time.time())

    def test_last_value_non_existent_host(self):
        """Récupération de 'lastvalue' sur un hôte non-configuré"""
        self.app.get(
            '/lastvalue?host=%s&ds=%s' % (
                'inexistent',
                'sysUpTime',
            ),
            status=404,
        )

    def test_last_value_file_not_found(self):
        """Récupération de 'lastvalue' avec un fichier inexistant"""
        self.app.get(
            '/lastvalue?host=%s&ds=%s' % (
                'testserver',
                'inexistent',
            ),
            status=404,
        )

    def test_last_value_nominal(self):
        """Récupération de 'lastvalue' : cas nominal"""
        response = self.app.get(
            '/lastvalue?host=%s&ds=%s' % (
                'testserver',
                'sysUpTime',
            ),
        )
        self.assertEqual(response.json['lastvalue'], 2.9426086420138886)

    def test_start_time_nominal(self):
        """Récupération de 'starttime' : cas nominal"""
        response = self.app.get('/starttime?host=testserver')
        self.assertEqual(response.json, {
            'starttime': 1232694600,
            'host': 'testserver',
        })

    def test_start_time_error(self):
        """Récupération de 'starttime' : avec une erreur"""
        response = self.app.get('/starttime?host=inexistent')
        self.assertEqual(response.json, {
            'starttime': 0,
            'host': 'inexistent',
        })

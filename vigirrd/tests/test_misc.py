# -*- coding: utf-8 -*-
"""
"""
import tg
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
            status=500,
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
        self.assertEqual(response.json['lastvalue'], 254241.38667000001)

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

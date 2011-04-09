# -*- coding: utf-8 -*-
# pylint: disable-msg=C0111,R0904

import time

from vigirrd.lib import conffile
from vigirrd.tests import TestController

class TestGraph(TestController):
    def setUp(self):
        super(TestGraph, self).setUp()
        conffile.reload()
        self.now = int(time.time())

    def test_graph_file_not_found(self):
        """Génération d'un graphe sur un hôte inexistant"""
        self.app.get(
            '/graph?host=%s&graphtemplate=%s' % (
                'inexistent',
                'inexistent',
            ),
            status=404,
        )

#    def test_graph_nominal_html(self):
#        """Récupération de 'lastvalue' : cas nominal"""
#        response = self.app.get(
#            '/lastvalue?host=%s&ds=%s' % (
#                'testserver',
#                'sysUpTime',
#            ),
#        )
#        self.assertEqual(response.json['lastvalue'], 254241.38667000001)

#    def test_graph_nominal_image(self):
#        """Récupération de 'lastvalue' : cas nominal"""
#        response = self.app.get(
#            '/lastvalue?host=%s&ds=%s' % (
#                'testserver',
#                'sysUpTime',
#            ),
#        )
#        self.assertEqual(response.json['lastvalue'], 254241.38667000001)

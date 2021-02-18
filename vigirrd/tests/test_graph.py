# -*- coding: utf-8 -*-
# pylint: disable-msg=C0111,R0904
# Copyright (C) 2006-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

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

    def test_graph_nominal_html(self):
        """Récupération de 'lastvalue' : cas nominal"""
        response = self.app.get(
            '/lastvalue?host=%s&ds=%s' % (
                'testserver',
                'sysUpTime',
            ),
        )
        self.assertTrue('lastvalue' in response.json)

    def test_graph(self):
        '''Génération d'un graphe à partir des données de métrologie.'''
        res = self.app.get('/graph.png', {
                'host': 'testserver',
                'graphtemplate': 'UpTime',
                'start': '1232694600',
                'duration': 3500,
            })
        self.assertEqual('image/png', res.content_type)

# -*- coding: utf-8 -*-
"""
"""
import tg
import time

from vigirrd.lib import conffile
from vigirrd.tests import TestController

class TestHTMLPages(TestController):
    def setUp(self):
        super(TestHTMLPages, self).setUp()
        conffile.reload()
        self.now = int(time.time())

    def test_index_default(self):
        """Page d'accueil sans arguments"""
        response = self.app.get('/index', status=302)
        response = response.follow()
        self.assertTrue(
            '<a href="/graphs.html?host=testserver">testserver</a>' in \
            response.body
        )

    def test_index_host(self):
        """Page d'accueil avec juste un hôte"""
        response = self.app.get('/index?host=testserver', status=302)
        response = response.follow()
        self.assertTrue(
            '<input type="radio" name="graphtemplate" value="UpTime" />' in \
            response.body
        )

    def test_servers(self):
        """Liste des hôtes supervisés"""
        response = self.app.get('/servers')
        self.assertTrue(
            '<a href="/graphs.html?host=testserver">testserver</a>' in \
            response.body
        )

    def test_graphs_html(self):
        """Liste des graphes d'un hôte au format HTML"""
        response = self.app.get('/graphs?host=testserver')
        self.assertTrue(
            '<input type="radio" name="graphtemplate" value="UpTime" />' in \
            response.body
        )

    def test_graphs_json(self):
        """Liste des graphes d'un hôte au format JSON"""
        response = self.app.get('/graphs.json?host=testserver', headers={
            'Content-Type': 'application/json',
        })
        self.assertEqual(response.json, {
            'host': 'testserver',
            'graphs': ['UpTime'],
        })

# -*- coding: utf-8 -*-
# pylint: disable-msg=C0111,R0904
# Copyright (C) 2006-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import time, urllib2

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
            u'<a href="/graphs.html?host=testserver">testserver</a>' in
            response.unicode_body
        )
        self.assertTrue(
            u'<a href="/graphs.html?host=testserver+%C3%A9%C3%A7%C3%A0">'
            u'testserver éçà</a>' in
            response.unicode_body
        )

    def test_index_host(self):
        """Page d'accueil avec juste un hôte"""
        response = self.app.get('/index?host=testserver', status=302)
        response = response.follow()
        self.assertTrue(
            '<input type="radio" name="graphtemplate" value="UpTime" />' in
            response.unicode_body
        )

    def test_index_host_unicode(self):
        """Page d'accueil avec juste un hôte (unicode)"""
        response = self.app.get('/index?host=%s' %
            urllib2.quote(u'testserver éçà'.encode('utf-8')),
            status=302)
        response = response.follow()
        self.assertTrue(
            u'<input type="radio" name="graphtemplate" value="UpTime éçà" />' in
            response.unicode_body
        )

    def test_servers(self):
        """Liste des hôtes supervisés"""
        response = self.app.get('/servers')
        self.assertTrue(
            '<a href="/graphs.html?host=testserver">testserver</a>' in
            response.unicode_body
        )

        self.assertTrue(
            u'<a href="/graphs.html?host=testserver+%C3%A9%C3%A7%C3%A0">'
            u'testserver éçà</a>' in
            response.unicode_body
        )

    def test_graphs_html(self):
        """Liste des graphes d'un hôte au format HTML"""
        response = self.app.get('/graphs?host=testserver')
        self.assertTrue(
            '<input type="radio" name="graphtemplate" value="UpTime" />' in
            response.body
        )

    def test_graphs_html_unicode(self):
        """Liste des graphes d'un hôte au format HTML (unicode)"""
        response = self.app.get('/graphs?host=%s' %
            urllib2.quote(u'testserver éçà'.encode('utf-8')))
        self.assertTrue(
            u'<input type="radio" name="graphtemplate" value="UpTime éçà" />' in
            response.unicode_body
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

    def test_graphs_json_unicode(self):
        """Liste des graphes d'un hôte au format JSON (unicode)"""
        response = self.app.get(
            '/graphs.json?host=%s' %
                urllib2.quote(u'testserver éçà'.encode('utf-8')),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.json, {
            'host': u'testserver éçà',
            'graphs': [u'UpTime éçà'],
        })

# -*- coding: utf-8 -*-
# pylint: disable-msg=C0111,R0904
# Copyright (C) 2006-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import time, urllib2

from vigirrd.lib import conffile
from vigirrd.tests import TestController

class TestExportCSV(TestController):
    def setUp(self):
        super(TestExportCSV, self).setUp()
        conffile.reload()
        # Dernière mesure disponible dans le fichier
        self.last = 1232874484 # Sun Jan 25 10:08:04 2009.
        self.host = 'testserver'
        self.datasource = 'UpTime'

    def tearDown(self):
        super(TestExportCSV, self).tearDown()

    def test_export_invalid_time(self):
        """Erreur 404 lors d'un export CSV avec dates dans le futur"""
        # Date dans le futur.
        now = int(time.time()) + 3600
        self.app.get(
            '/export?host=%s&graphtemplate=%s&start=%d' % (
                self.host,
                self.datasource,
                now,
            ), status=404
        )

    def test_export_no_start(self):
        """Export CSV sans 'start'"""
        self.app.get(
            '/export?host=%s&graphtemplate=%s&end=%d' % (
                self.host,
                self.datasource,
                int(time.time()),
            ),
        )

    def test_export_no_end(self):
        """Export CSV sans 'end'"""
        start = self.last - 86400 # On remonte d'1j dans le fichier RRD.
        resp = self.app.get(
            # Simule en prime un client qui se connecte
            # depuis le fuseau horaire de Berlin/Paris/Madrid.
            '/export?host=%s&graphtemplate=%s&start=%d&timezone=-60' % (
                self.host,
                self.datasource,
                start,
            ),
        )
        rows = [row.strip().split(';') for row in resp.body.strip().split('\n')]
        # On s'attend à avoir 14 lignes de données + l'en-tête.
        self.assertEqual(len(rows), 15)
        # On doit avoir 3 colonnes : Timestamp + Date + PDS(sysUpTime).
        self.assertEqual(len(rows[0]), 3)
        # On vérifie les en-têtes, la 1ère date et la dernière date du fichier.
        self.assertEqual(rows[0][0], '"Timestamp"')
        self.assertEqual(rows[0][1], '"Date"')
        self.assertEqual(
            rows[0][2],
            '"sys%s"' % urllib2.unquote(self.datasource)
        )
        # L'export ne donne qu'1h de données par défaut.
        self.assertEqual(rows[1][0],   '"%d"' % 1232788084)
        self.assertEqual(rows[-1][0],  '"%d"' % 1232791685)
        # Support des différentes versions de Babel
        try:
            self.assertEqual(rows[1][1],   '"January 24, 2009 10:08:04 AM +0100"')
            self.assertEqual(rows[-1][1],  '"January 24, 2009 11:08:05 AM +0100"')
        except AssertionError:
            self.assertEqual(rows[1][1],   '"January 24, 2009 at 10:08:04 AM +0100"')
            self.assertEqual(rows[-1][1],  '"January 24, 2009 at 11:08:05 AM +0100"')

    def test_export_using_default_values(self):
        """Export CSV sans 'start' ni 'end'"""
        self.app.get(
            '/export?host=%s&graphtemplate=%s' % (
                self.host,
                self.datasource,
            ),
        )

class TestExportCSVUnicode(TestExportCSV):
    """
    Exécute la même batterie de tests, mais en utilisant un nom d'hôte
    et un nom de donnée de performance avec des caractères accentués
    (en unicode).
    """
    def setUp(self):
        super(TestExportCSVUnicode, self).setUp()
        self.host = urllib2.quote(u'testserver éçà'.encode('utf-8'))
        self.datasource = urllib2.quote(u'UpTime éçà'.encode('utf-8'))

    def shortDescription(self):
        desc = super(TestExportCSVUnicode, self).shortDescription()
        return desc + ' (unicode)'

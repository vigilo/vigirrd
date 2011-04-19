# -*- coding: utf-8 -*-
# pylint: disable-msg=C0111,R0904
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import time

from vigirrd.lib import conffile
from vigirrd.tests import TestController

class TestExportCSV(TestController):

    def setUp(self):
        super(TestExportCSV, self).setUp()
        conffile.reload()
        self.now = int(time.time())

    def tearDown(self):
        super(TestExportCSV, self).tearDown()

    def test_export_invalid_time(self):
        """Erreur 404 lors d'un export CSV pour les dates dans le futur"""
        # Date dans le futur.
        now = int(time.time()) + 3600
        self.app.get(
            '/export?host=%s&graphtemplate=%s&start=%d' % (
                'testserver',
                'UpTime',
                now,
            ), status=404
        )

    def test_export_no_start(self):
        """Export CSV sans 'start'"""
        self.app.get(
            '/export?host=%s&graphtemplate=%s&end=%d' % (
                'testserver',
                'UpTime',
                self.now,
            ),
        )

    def test_export_no_end(self):
        """Export CSV sans 'end'"""
        self.app.get(
            '/export?host=%s&graphtemplate=%s&start=%d' % (
                'testserver',
                'UpTime',
                self.now - 86400,
            ),
        )

    def test_export_using_default_values(self):
        """Export CSV sans 'start' ni 'end'"""
        self.app.get(
            '/export?host=%s&graphtemplate=%s' % (
                'testserver',
                'UpTime',
            ),
        )

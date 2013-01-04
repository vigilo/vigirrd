# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# pylint: disable-msg=C0111,R0904
# Copyright (C) 2006-2013 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os
import time
import tempfile
import shutil
from unittest import TestCase

import networkx as nx
import tg
from vigilo.common import get_rrd_path
from vigirrd import model
from vigirrd.lib import rrd, conffile
from vigirrd.tests import TestController

class TestRRDclass(TestController):
    """Test the module-level functions in RRDGraph"""

    def setUp(self):
        """Called before every test case."""
        # Loading the application:
        super(TestRRDclass, self).setUp()

        # spécifique VigiRRD
        conffile.reload()
        dsname = "sysUpTime"
        rrdfilename = os.path.join(tg.config['rrd_base'], "testserver",
                                   "%s.rrd" % dsname)
        self.rrd = rrd.RRD(rrdfilename, "testserver")

    def tearDown(self):
        """Called after every test case."""
        super(TestRRDclass, self).tearDown()

    def test_getstep(self):
        '''Récupération du pas dans les données de métrologie.'''
        step = 300

        result = None
        if self.rrd is not None:
            result = self.rrd.getStep()
        self.assertEqual(result, step, "getStep() does not work")

    def test_getstarttime(self):
        '''Détection de l'heure de début des données de performance.'''

        value = 1232694600

        result = None
        if self.rrd is not None:
            result = self.rrd.getStartTime()

        self.assertEqual(result, value, "getStartTime() does not work")

    def test_fetchdata(self):
        '''Récupération des données de métrologie d'une source.'''
        answer = {
            1232695200: [75141.386666999999, None],
            1232697600: [77541.0, None],
            1232696100: [76041.386666999999, None],
            1232694600: [74541.386666999999, None],
            1232697900: [77841.386666999999, None],
            1232695500: [75442.0, None],
            1232696400: [76342.0, None],
            1232697000: [76942.0, None],
            1232694900: [74841.613333000001, None],
            1232695800: [75741.613333000001, None],
            1232697300: [77241.613333000001, None],
            1232696700: [76642.0, None],
        }

        result = None
        if self.rrd is not None:
            result = self.rrd.fetchData("DS")

        self.assertEqual(result, answer, "fetchData() does not work")

    def test_graph(self):
        '''Génération d'un graphe à partir des données de métrologie.'''
        tmpdir = tempfile.mkdtemp()
        tmpfile = os.path.join(tmpdir, "graph.svg")

        #graphfile = os.path.join(tg.config["rrd_base"],
        #                         "testserver", "graph.svg")
        start = 1232694600
        duration = 3500

        try:
            # La bibliothèque de manipulation des fichiers RRS
            # doit avoir été chargée correctement.
            self.assertTrue(self.rrd is not None)

            #print [pds.name for pds in model.DBSession.query(model.PerfDataSource).all()]
            ds = model.PerfDataSource.by_name("sysUpTime")
            self.rrd.graph(conffile.templates["lines"], [ds, ], format="SVG",
                outfile=tmpfile, start=start, duration=duration)

            # L'ancien test vérifiait le contenu du graphe généré,
            # néanmoins le résultat varie beaucoup en fonction de
            # la version de rrdtool utilisée et d'autres bibliothèques
            # du système. On se contente donc de vérifier l'existence
            # du graphe.
            self.assertTrue(os.path.exists(tmpfile))
        finally:
            shutil.rmtree(tmpdir)

    def test_getLastValue(self):
        '''Récupération de la dernière valeur de métrologie dans un RRD.'''
        result = None
        if self.rrd is not None:
            result = self.rrd.getLastValue("sysUpTime")
        answer = 2.9426086420138886
        self.assertEqual(result, answer, "getLastValue() does not work")

    def test_exportCSV(self):
        '''Export des données au format CSV.'''
        server = 'testserver'
        graphtemplate = 'UpTime'
        indicator = 'All'
        # On se place à un emplacement du fichier
        # où l'on sait qu'il y a des données.
        start = 1232000000
        end = 1232010000

        csv_data = """
"Timestamp";"Date";"sysUpTime"
"1232000001";"January 15, 2009 6:13:21 AM +0000";"9658471.000000"
"1232001801";"January 15, 2009 6:43:21 AM +0000";"9660271.000000"
"1232003601";"January 15, 2009 7:13:21 AM +0000";"9662071.000000"
"1232005401";"January 15, 2009 7:43:21 AM +0000";"9663871.000000"
"1232007201";"January 15, 2009 8:13:21 AM +0000";"9665671.000000"
"""[1:]
        output = rrd.exportCSV(server, graphtemplate,
                        indicator, start, end, 0)

        # On compare l'export au résultat attendu.
        normalized_output = output.replace("\r\n", "\n")
        self.assertEqual(csv_data, normalized_output)



class SortDSTestCase(TestController):
    """
    Tri d'une liste de définitions de RRD (fonction RRD._sort_defs())
    """

    def setUp(self):
        # Loading the application:
        super(SortDSTestCase, self).setUp()

        # spécifique VigiRRD
        conffile.reload()
        rrdfilename = get_rrd_path("testserver", "sysUpTime",
                                   base_dir=tg.config['rrd_base'],
                                   path_mode=tg.config["rrd_path_mode"])
        rrdfilenames = {
            "DS1": rrdfilename,
            "DS2": rrdfilename,
        }
        self.rrd = rrd.RRD(rrdfilenames, "testserver")
        self.template = {"cdefs": [], "draw":
                    [{ "type": "LINE1", "color": "#EE0088" },
                     { "type": "LINE1", "color": "#FF5500" }],
               }

    def tearDown(self):
        super(SortDSTestCase, self).tearDown()

    def _get_sorted_defs(self, ds_list):
        defs = []
        for i in range(len(ds_list)):
            defs.extend(self.rrd.get_def(ds_list, i, self.template,
                                         int(time.time())))
        print "defs:", defs
        sorted_defs = self.rrd._sort_defs(defs, ds_list)
        print "sorted:", sorted_defs
        return sorted_defs

    def test_no_deps(self):
        "Tri: DEF avant CDEF"
        ds1 = model.PerfDataSource(name="DS1", factor=1)
        ds2 = model.PerfDataSource(name="DS2", factor=1)
        ds_list = [ds1, ds2]
        sorted_defs = self._get_sorted_defs(ds_list)
        keys = [ d.split("=")[0] for d in sorted_defs ]
        expected = ['DEF:data_0_orig', 'DEF:data_1_orig',
                    'CDEF:data_1', 'CDEF:data_0']
        self.assertEqual(keys, expected)

    def test_internal_deps(self):
        """
        Tri sur une liste avec dépendance sur un autre DS de la liste
        """
        ds1 = model.PerfDataSource(name="DS1", factor=1)
        ds2 = model.PerfDataSource(name="DS2", factor=1)
        cdef1 = model.Cdef(name="DS1", cdef="DS2,8,*")
        self.template["cdefs"] = [cdef1]
        ds_list = [ds1, ds2]
        sorted_defs = self._get_sorted_defs(ds_list)
        keys = [ d.split("=")[0] for d in sorted_defs ]
        expected = ['DEF:data_1_orig', 'CDEF:data_1',
                    'CDEF:data_0_orig', 'CDEF:data_0']
        self.assertEqual(keys, expected)

    def test_external_deps(self):
        """
        Tri sur une liste avec dépendance sur un DS hors de la liste
        """
        ds1 = model.PerfDataSource(name="DS1", factor=1)
        cdef1 = model.Cdef(name="DS1", cdef="DS2,8,*")
        self.template["cdefs"] = [cdef1]
        ds_list = [ds1]
        sorted_defs = self._get_sorted_defs(ds_list)
        keys = [ d.split("=")[0] for d in sorted_defs ]
        expected = ['DEF:data_0_source', 'CDEF:data_0_orig', 'CDEF:data_0']
        self.assertEqual(keys, expected)
        # on vérifie qu'il a bien généré le DEF pour la source non affichée
        self.assertTrue(sorted_defs[0].endswith("testserver/DS2.rrd:DS:AVERAGE"))

    def test_internal_and_external_deps(self):
        """
        Tri sur une liste avec dépendances internes et externes
        """
        # Comme le test ucd/RAM
        ds1 = model.PerfDataSource(name="DS1", factor=1)
        ds2 = model.PerfDataSource(name="DS2", factor=1)
        ds3 = model.PerfDataSource(name="DS3", factor=1)
        cdef1 = model.Cdef(name="DS1", cdef="DS2,8,*")
        cdef2 = model.Cdef(name="DS3", cdef="DS4,DS2,-,DS1,-")
        self.template["cdefs"] = [cdef1, cdef2]
        ds_list = [ds3, ds1, ds2]
        sorted_defs = self._get_sorted_defs(ds_list)
        keys = [ d.split("=")[0] for d in sorted_defs ]
        expected = ['DEF:data_2_orig', 'CDEF:data_2',
                    'CDEF:data_1_orig', 'CDEF:data_1',
                    'DEF:data_0_source', 'CDEF:data_0_orig', 'CDEF:data_0']
        self.assertEqual(keys, expected)

    def test_cycle(self):
        """
        Détection d'un cycle dans les dépendances de la liste
        """
        # Comme le test ucd/RAM
        ds1 = model.PerfDataSource(name="DS1", factor=1)
        cdef1 = model.Cdef(name="DS1", cdef="DS1,8,*")
        self.template["cdefs"] = [cdef1]
        ds_list = [ds1]
        self.assertRaises(nx.NetworkXUnfeasible, self._get_sorted_defs, ds_list)

class TestRRDclassCF(TestController):
    def test_getPeriodCF(self):
        """
        Récupération de la fonction de consolidation adéquate
        """
        conffile.reload()
        days = 86400
        rrdfile = rrd.RRD(
            os.path.join(tg.config['rrd_base'], "testserver", "cf.rrd"),
            "testserver"
        )
        ts = int(time.time())

        # Récupération de la fonction de consolidation pour l'archive
        # la plus précise : il doit s'agir de "LAST".
        self.assertEquals(rrdfile.getPeriodCF(ts - 1 * days), "LAST")

        # En revanche, pour l'archive juste après, il doit s'agit d' "AVERAGE".
        self.assertEquals(rrdfile.getPeriodCF(ts - 3 * days), "AVERAGE")

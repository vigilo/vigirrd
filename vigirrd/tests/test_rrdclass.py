# -*- coding: utf-8 -*-
import os
import platform
import unittest
import tempfile
import shutil
import filecmp
from pprint import pprint

import tg
from paste.deploy import loadapp
from webtest import TestApp

from vigirrd.lib import rrd, conffile


class RRDclass(unittest.TestCase):
    """Test the module-level functions in RRDGraph"""

    application_under_test = 'main_without_authn'

    def __init__(self, *args, **kwargs):
        """Initialisation"""
        super(RRDclass, self).__init__(*args, **kwargs)

        # indicateur architecture
        self.a64 = (platform.machine() != 'i686')

        # repertoire pour donnees selon architecture
        self.dir_a = "."
        if self.a64:
            self.arch = "64"
        else:
            self.arch = "32"

    def setUp(self):
        """Call before every test case."""
        # Loading the application:
        conf_dir = tg.config.here
        wsgiapp = loadapp('config:test.ini#%s' % self.application_under_test,
                          relative_to=conf_dir)
        self.app = TestApp(wsgiapp)
        # Setting it up:
        test_file = os.path.join(conf_dir, 'test.ini')
        # spécifique VigiRRD
        conffile.reload()
        rrd_base = os.path.join(tg.config.get("rrd_base"), "rrd%s" % self.arch)
        tg.config["rrd_base"] = rrd_base
        filename = "sysUpTime.rrd"
        rrdfilename = os.path.join(rrd_base, "testserver", filename)
        self.rrd = rrd.RRD(rrdfilename, "testserver")

    def tearDown(self):
        """Call after every test case."""
        pass

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

    def test_getds(self):
        '''Récupération de la configuration d'une source de données.'''

        answer = {'DS': {'min': None, 'max': None, 'unknown_sec': 0,
                             'minimal_heartbeat': 600, 'value': 46814384.0,
                             'ds_name': 'DS', 'type': 'GAUGE', 'last_ds': '254426',
                            } }

        result = None
        if self.rrd is not None:
            result = self.rrd.getDS()

        self.assertEqual(result, answer, "getDS() does not work")

    def test_listds(self):
        '''Liste des sources de données d'un fichiers RRD.'''
        result = None
        if self.rrd is not None:
            result = self.rrd.listDS()
        self.assertEqual(result, ["DS"], "listDS() does not work")

    def test_fetchdata(self):
        '''Récupération des données de métrologie d'une source.'''
        answer = {
                  1232694600: [74541.386666666673, None],
                  1232694900: [74841.613333333327, None],
                  1232695200: [75141.386666666673, None],
                  1232695500: [75442.0, None],
                  1232695800: [75741.613333333327, None],
                  1232696100: [76041.386666666673, None],
                  1232696400: [76342.0, None],
                  1232696700: [76642.0, None],
                  1232697000: [76942.0, None],
                  1232697300: [77241.613333333327, None],
                  1232697600: [77541.0, None],
                  1232697900: [77841.386666666673, None],
                 }

        result = None
        if self.rrd is not None:
            result = self.rrd.fetchData("DS")

        self.assertEqual(result, answer, "fetchData() does not work")

    def test_graph(self):
        '''Génération d'un graphe à partir des données de métrologie.'''
        tmpdir = tempfile.mkdtemp()
        tmpfile = os.path.join(tmpdir, "graph.svg")

        graphfile = os.path.join(tg.config["rrd_base"],
                                 "testserver", "graph.svg")
        start = 1232694600
        duration = 3500

        result = None
        if self.rrd is not None:
            self.rrd.graph(conffile.templates["lines"], ["DS"], format="SVG",
                outfile=tmpfile, start=start, duration=duration)
            if os.path.exists(tmpfile):
                # Comparaison du graphe généré avec le graphe de référence.
                result = filecmp.cmp(tmpfile, graphfile)
        shutil.rmtree(tmpdir)
        self.assertEqual(result, True, "The generated graph is different")

    def test_getLastValue(self):
        '''Récupération de la dernière valeur de métrologie dans un RRD.'''
        result = None
        if self.rrd is not None:
            result = self.rrd.getLastValue()
        self.assertEqual(result, None, "getLastValue() does not work")

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
"Timestamp";"sysUpTime"
"1232000001";"9658471.0"
"1232001801";"9660271.0"
"1232003601";"9662071.0"
"1232005401";"9663871.0"
"1232007201";"9665671.0"
"""[1:]
        output = rrd.exportCSV(server, graphtemplate,
                        indicator, start, end)

        # On compare l'export au résultat attendu.
        normalized_output = output.replace("\r\n", "\n")
        self.assertEqual(csv_data, normalized_output)

# vim:set expandtab tabstop=4 shiftwidth=4:

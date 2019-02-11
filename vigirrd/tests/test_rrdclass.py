# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# pylint: disable-msg=C0111,R0904
# Copyright (C) 2006-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

from __future__ import print_function
import os
import time
import tempfile
import shutil
from unittest import TestCase
from types import ModuleType
from datetime import datetime

import networkx as nx
from tg.util import ContextObj
from tg import request_local, config
from tg.support.registry import StackedObjectProxy, RegistryManager
from tg.wsgiapp import RequestLocals
from tg.i18n import _get_translator
from webtest import TestApp
import pytz
import babel.dates

from vigilo.common import get_rrd_path
from vigirrd import model
from vigirrd.lib import rrd, conffile
from vigirrd.tests import TestController


class CallWrapperApp(object):
    def __init__(self, obj, func, *args, **kw):
        self.obj = obj
        self.func = func
        self.args = args
        self.kw = kw
        self.content_type = 'text/plain'
        self.status = '200 OK'

    def __call__(self, environ, start_response):
        if 'paste.registry' in environ:
            conf = config._current_obj()
            req = request_local.Request(environ)
            req._fast_setattr('_language', conf['lang'])
            req._fast_setattr('_response_type', None)

            ctx = RequestLocals()
            ctx.response = request_local.Response()
            ctx.request = req
            ctx.translator = _get_translator(conf['lang'], tg_config=conf)
            ctx.config = conf

            registry = environ['paste.registry']
            registry.register(request_local.config, conf)
            registry.register(request_local.context, ctx)

        response_headers = [('Content-type', self.content_type)]
        start_response(self.status, response_headers)

        # Rebinding de la méthode sur son objet si nécessaire.
        if isinstance(self.obj, ModuleType):
            desc = self.func
        else:
            desc = self.func.__get__(self.obj, type(self.obj))

        res = desc(*self.args, **self.kw)
        if not isinstance(res, str):
            res = unicode(res).encode('utf-8')
        return [res]


class TestRRDclass(TestController):
    """Test the module-level functions in RRDGraph"""

    def setUp(self):
        """Called before every test case."""
        # Loading the application:
        super(TestRRDclass, self).setUp()

        # spécifique VigiRRD
        conffile.reload()
        dsname = "sysUpTime"
        rrdfilename = os.path.join(config['rrd_base'], "testserver",
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

        start = 1232694600
        duration = 3500

        try:
            # La bibliothèque de manipulation des fichiers RRD
            # doit avoir été chargée correctement.
            self.assertTrue(self.rrd is not None)

            ds = model.PerfDataSource.by_name("sysUpTime")
            wsgiapp = CallWrapperApp(self.rrd, self.rrd.graph,
                                     conffile.templates["lines"], [ds, ],
                                     format="SVG", outfile=tmpfile,
                                     start=start, duration=duration)
            wsgiapp = RegistryManager(wsgiapp)
            app = TestApp(wsgiapp)
            app.get('/')

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

        # Permet de gommer les différences de formatage des dates
        # liées aux changements de version de Babel.
        date_formatter = lambda ts: babel.dates.format_datetime(
            pytz.utc.localize(
                datetime.utcfromtimestamp(ts)
            ).astimezone(pytz.FixedOffset(0)),
            'long', locale='en_US')
        dates = map(date_formatter, [1232000001, 1232001801, 1232003601, 1232005401, 1232007201])

        # La sortie attendue est la suivante :
        csv_data = """
"Timestamp";"Date";"sysUpTime"
"1232000001";"%s";"9658471.000000"
"1232001801";"%s";"9660271.000000"
"1232003601";"%s";"9662071.000000"
"1232005401";"%s";"9663871.000000"
"1232007201";"%s";"9665671.000000"
"""
        csv_data = csv_data[1:] % tuple(dates)

        wsgiapp = CallWrapperApp(rrd, rrd.exportCSV,
                                 server, graphtemplate,
                                 indicator, start, end, 0)
        wsgiapp = RegistryManager(wsgiapp)
        app = TestApp(wsgiapp)
        output = app.get('/').body

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
                                   base_dir=config['rrd_base'],
                                   path_mode=config["rrd_path_mode"])
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
        print("defs:", defs)
        sorted_defs = self.rrd._sort_defs(defs, ds_list)
        print("sorted:", sorted_defs)
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
            os.path.join(config['rrd_base'], "testserver", "cf.rrd"),
            "testserver"
        )
        ts = int(time.time())

        # Récupération de la fonction de consolidation pour l'archive
        # la plus précise : il doit s'agir de "LAST".
        self.assertEqual(rrdfile.getPeriodCF(ts - 1 * days), "LAST")

        # En revanche, pour l'archive juste après, il doit s'agit d' "AVERAGE".
        self.assertEqual(rrdfile.getPeriodCF(ts - 3 * days), "AVERAGE")

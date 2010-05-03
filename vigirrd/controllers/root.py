# -*- coding: utf-8 -*-
"""Main Controller"""

import os
import time
import re
from StringIO import StringIO
from logging import getLogger
LOGGER = getLogger(__name__)

import pylons
from tg import expose, flash, require, url, request, redirect, config, response
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPError, HTTPNotFound
from tg.controllers import CUSTOM_CONTENT_TYPE

from vigirrd.lib.base import BaseController
#from vigirrd.model import DBSession, metadata
from vigirrd.controllers.error import ErrorController

from vigirrd.lib import conffile
from vigirrd.lib import rrd

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the vigirrd application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
    
    error = ErrorController()

    @expose()
    def index(self, **kwargs):
        """Point d'entrée principal"""
        conffile.reload()
        if not conffile.hosts:
            raise HTTPError("No configuration yet")
        if "host" not in kwargs:
            redirect(url('/servers'))
            return
        host = kwargs["host"]
        if "graphtemplate" not in kwargs:
            redirect(url('/graphs'))
            return
        if "start" in kwargs:
            start = int(kwargs["start"])
        else:
            start = int(time.time()) - 86400 # Par défaut: 24 heures avant
        details = "1"
        if "details" in kwargs and not (kwargs["details"]):
            details = ""
        if "duration" not in kwargs:
            duration = 86400
        qs = "host=%s&graphtemplate=%s&start=%d&duration=%s&details=%s" \
                % (kwargs["host"], kwargs["graphtemplate"], start, duration, details)
        if "direct" in kwargs and kwargs["direct"]:
            redirect(url('/graph.png?%s' % qs))
            return
        else:
            redirect(url('/graph.html?%s' % qs))
            return

    @expose("json")
    def starttime(self, host):
        try:
            value = rrd.getStartTime(str(host))
        except rrd.RRDError:
            value = 0
        return {"starttime": value,
                "host": host}

    @expose("servers.html")
    def servers(self):
        conffile.reload()
        servers = conffile.hosts.keys()
        return {"servers": servers}

    @expose("graphs.html")
    @expose("json")
    def graphs(self, host):
        conffile.reload()
        graphtemplates = conffile.hosts[host]["graphes"].keys()
        graphtemplates.sort()
        if pylons.request.response_type == 'application/json':
            return graphtemplates
        return {"host": host,
                "graphs": graphtemplates,
               }

    @expose("graph.html", content_type=CUSTOM_CONTENT_TYPE)
    def graph(self, **kwargs):
        details = True
        if "details" in kwargs and not kwargs["details"]:
            details = False
        if "duration" not in kwargs:
            kwargs["duration"] = 86400
        duration = int(kwargs["duration"])
        start = int(kwargs["start"])
        filename = "%s_%s_%s_%s_%d.png" % (kwargs["host"],
                                           re.sub(r"[^\w]", "", kwargs["graphtemplate"]),
                                           start,
                                           duration,
                                           int(details)
                                           )
        image_file = os.path.join(config.get("image_cache_dir"), filename)
        try:
            rrd.showMergedRRDs(kwargs["host"], kwargs["graphtemplate"],
                               image_file, start, duration, details=details)
        except rrd.RRDNoDSError, e:
            raise HTTPError(str(e))
        except rrd.RRDNotFoundError, e:
            #raise HTTPNotFound("No RRD: %s" % str(e))
            redirect(url('/error'), code=404, message="<p>No RRD: %s</p>" % str(e))
            return
        if pylons.request.response_type == 'image/png':
            response.headers["Content-Type"] = "image/png"
            response.headers['Pragma'] = 'no-cache'
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Expires'] = '-1'
            result = StringIO()
            image = open(image_file, "rb")
            result.write(image.read())
            image.close()
            return result.getvalue()
        else:
            imgurl = os.path.join(config.get("image_cache_url", "/"),
                                   os.path.basename(image_file))
            return {"host": kwargs["host"],
                    "imgurl": imgurl,
                    "template": kwargs["graphtemplate"],
                   }

    @expose("json")
    def lastvalue(self, host, ds):
        conffile.reload()
        server = conffile.hosts[host]
        if not server:
            redirect(url('/error'), code=500,
                     message='<p>Host definition is empty</p>')
            return
        filename = rrd.getEncodedFileName(host, ds)
        if not filename or not os.path.exists(filename):
            #raise HTTPNotFound('The datasource "%s" does not exist, or has never been collected yet.' % ds)
            redirect(url('/error'), code=404,
                     message='<p>The datasource "%s" does not exist, or '
                             'has never been collected yet.</p>' % ds)
            return
        rrdfile = rrd.RRD(filename=str(filename), server=str(host))
        return {"lastvalue": rrdfile.getLastValue(),
                "host": host,
                "ds": ds
                }

    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def export(self, host, graphtemplate, ds=None, start=None, end=None):
        '''
        export CSV

        # valeurs finales -> dictionnaire
        # - renseigné a partir dictionnaires obtenus pour chaque indicateur
        # - sous la forme :
        #   * cle = indice
        #   * valeur = [TimeStamp, donnee dictionnaire1 pour TimeStamp, ..., 
        #     donnee dictionnaireN pour TimeStamp

        @param host: serveur
        @type  host: C{str}
        @param graphtemplate: graphe
        @type  graphtemplate: C{str}
        @param ds: indicateur graphe
        @type  ds: C{str}
        @param start: debut plage export
        @type  start: C{str}
        @param end: fin plage export
        @type  end: C{str}
        '''
        if not start:
            start = time.time() - 86400 # Par défaut: 24 heures avant
        start = int(start)
        now = int(time.time())
        if start >= now:
            redirect(url('/error'), code=404, message='<p>No data yet</p>')
            return
        if end is None:
            # one hour plus one second, start should be 1 sec in the past
            end = start + 3600 + 1
        else:
            end = int(end)
        if end > now:
            LOGGER.debug("exporting until %d instead of %d" % (now, end))
            end = now
        if ds:
            filename = rrd.getExportFileName(host, ds, start, end)
        else:
            filename = rrd.getExportFileName(host, graphtemplate, start, end)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment;filename=%s' % filename
        return rrd.exportCSV(host, graphtemplate, ds, start, end)


# -*- coding: utf-8 -*-
# pylint: disable-msg=R0201,R0913
# Copyright (C) 2006-2013 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Main Controller"""

import os
import time
import re
from StringIO import StringIO
from logging import getLogger
LOGGER = getLogger(__name__)

import pylons
from tg import expose, url, redirect, config, response
from pylons.i18n import ugettext as _
from tg.exceptions import HTTPServiceUnavailable, HTTPNotFound
from tg.controllers import CUSTOM_CONTENT_TYPE

from vigilo.turbogears.controllers import BaseController
from vigilo.turbogears.controllers.custom import CustomController
from vigilo.turbogears.controllers.error import ErrorController

from vigirrd.lib import conffile
from vigirrd.lib import rrd
from vigirrd.model import DBSession, Host

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
    custom = CustomController()

    def __init__(self, *args, **kw):
        super(RootController, self).__init__(*args, **kw)
        # Utilisation de rrdcached
        rrdcached = config.get("rrdcached", None)
        if rrdcached is not None:
            if os.path.exists(rrdcached) and os.access(rrdcached, os.W_OK):
                os.environ["RRDCACHED_ADDRESS"] = rrdcached
            else:
                LOGGER.warning(_("No access to the rrdcached socket: %s"),
                               rrdcached)


    @expose()
    def index(self, **kwargs):
        """Point d'entrée principal"""
        if not DBSession.query(Host).count():
            LOGGER.error("No configuration yet")
            raise HTTPServiceUnavailable("No configuration yet")
        if "host" not in kwargs:
            return redirect('/servers')

        host = kwargs["host"]
        if "graphtemplate" not in kwargs:
            return redirect('/graphs', host_=host)

        if "start" in kwargs:
            start = int(kwargs["start"])
        else:
            start = int(time.time()) - 86400 # Par défaut: 24 heures avant

        details = "1"
        if "details" in kwargs and kwargs["details"] == "0":
            details = ""
        duration = int(kwargs.get('duration', 86400))

        if "direct" in kwargs and kwargs["direct"]:
            format = "png"
        else:
            format = "html"

        redirect('/graph.%s' % format, {
            'host_': kwargs['host'],
            'graphtemplate': kwargs['graphtemplate'],
            'start': start,
            'duration': duration,
            'details': details,
        })

    @expose("json")
    def starttime(self, host, nocache=None): # pylint: disable-msg=W0613
        try:
            value = rrd.getStartTime(str(host))
        except rrd.RRDError:
            value = 0
        return {
            "starttime": value,
            "host": host
        }

    @expose("servers.html")
    def servers(self):
        servers = [ h.name for h in DBSession.query(Host.name).all() ]
        return {"servers": servers}

    @expose("graphs.html")
    @expose("json")
    def graphs(self, host):
        host = Host.by_name(host)
        if not host:
            raise HTTPNotFound()
        graphtemplates = [ g.name for g in host.graphs ]
        graphtemplates.sort()
        return {
            "host": host.name,
            "graphs": graphtemplates,
       }

    @expose("graph.html", content_type=CUSTOM_CONTENT_TYPE)
    def graph(self, **kwargs):
        conffile.reload()
        # Par défaut, la légende est affichée.
        # Passer details=0 pour la désactiver.
        try:
            details = bool(int(kwargs.get('details', 1)))
        except ValueError:
            details = True

        try:
            timezone = int(kwargs.get('timezone'))
        except (ValueError, TypeError):
            # time.timezone utilise la notation POSIX dans laquelle
            # la direction du temps est inversée
            # (ie. UTC+01:00 = -3600 secondes).
            # Note: time.daylight indique juste que la timezone actuelle
            # supporte le changement d'heure DST, pas qu'il est actif,
            # il faut recourir à localtime() pour avoir cette information.
            if time.daylight and time.localtime().tm_isdst:
                timezone = -time.altzone / 60
            else:
                timezone = -time.timezone / 60

        # La durée par défaut est de 86400 secondes (1 journée).
        duration = int(kwargs.get("duration", 86400))
        # Si la durée est 0, vigirrd.lib.rrd utilise la date courante
        # comme date de fin. Si les machines ne sont pas synchronisées,
        # ceci provoque une erreur dans RRDtool (date début > date fin).
        if duration < 1:
            duration = 1

        # Par défaut, on prend la dernière tranche horaire.
        start = int(kwargs.get("start", time.time() - duration))
        # Dans le cas où la date se situe avant l'Epoch, on borne.
        # RRDtool rejetterait une telle date de toutes façons.
        if start < 0:
            start = 0

        filename = "%s_%s_%s_%s_%d.png" % (kwargs["host"],
                                           re.sub(r"[^\w]", "",
                                                kwargs["graphtemplate"]),
                                           start,
                                           duration,
                                           int(details)
                                           )
        image_file = os.path.join(config.get("image_cache_dir"), filename)
        try:
            rrd.showMergedRRDs(kwargs["host"], kwargs["graphtemplate"],
                               image_file, start, duration, details=details,
                               timezone=timezone)
        except rrd.RRDNoDSError, e:
            raise HTTPServiceUnavailable(str(e))
        except rrd.RRDNotFoundError, e:
            raise HTTPNotFound("No RRD: %s" % str(e))
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
            imgurl = "/%s" % os.path.basename(image_file)
            return {"host": kwargs["host"],
                    "imgurl": url(imgurl),
                    "template": kwargs["graphtemplate"],
                   }

    @expose("json")
    def lastvalue(self, host, ds, nocache=None): # pylint: disable-msg=W0613
        server = Host.by_name(host)
        if not server:
            raise HTTPNotFound("Unknown host: %s" % host)
        filename = rrd.getEncodedFileName(host, ds)
        if not filename or not os.path.exists(filename):
            raise HTTPNotFound('The datasource "%s" does not exist, '
                'or has never been collected yet.' % ds)
        rrdfile = rrd.RRD(filename=str(filename), server=str(host))
        return {"lastvalue": rrdfile.getLastValue(ds),
                "host": host,
                "ds": ds
                }

    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def export(self, host, graphtemplate, ds=None,
        start=None, end=None, timezone=None,
        nocache=None): # pylint: disable-msg=W0613
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
        @param timezone: décalage en minutes entre l'heure UTC
            et l'heure dans le fuseau horaire de l'utilisateur
            (p.ex. 60 = UTC+01).
        @type  timezone: C{str}
        @param nocache: Valeur aléatoire (généralement un horodatage UNIX)
            destinée à empêcher la mise en cache du fichier exporté par le
            navigateur.
        @type  nocache: C{str}
        '''
        if not start:
            start = time.time() - 86400 # Par défaut: 24 heures avant
        start = int(start)
        now = int(time.time())

        try:
            timezone = int(timezone)
        except (ValueError, TypeError):
            # time.timezone utilise la notation POSIX dans laquelle
            # la direction du temps est inversée
            # (ie. UTC+01:00 = -3600 secondes).
            # Note: time.daylight indique juste que la timezone actuelle
            # supporte le changement d'heure DST, pas qu'il est actif,
            # il faut recourir à localtime() pour avoir cette information.
            if time.daylight and time.localtime().tm_isdst:
                timezone = -time.altzone / 60
            else:
                timezone = -time.timezone / 60

        if start >= now:
            raise HTTPNotFound('No data yet')
        if Host.by_name(host) is None:
            raise HTTPNotFound("No such host")
        if end is None:
            # one hour plus one second, start should be 1 sec in the past
            end = start + 3600 + 1
        else:
            end = int(end)
        if end > now:
            LOGGER.debug("exporting until %d instead of %d" % (now, end))
            end = now
        if ds:
            filename = rrd.getExportFileName(host, ds, start, end,
                                                timezone=timezone)
        else:
            filename = rrd.getExportFileName(host, graphtemplate, start, end,
                                                timezone=timezone)

        # Sans les 2 en-têtes suivants qui désactivent la mise en cache,
        # Internet Explorer refuse de télécharger le fichier CSV (cf. #961).
        response.headers['Pragma'] = 'public'           # Nécessaire pour IE.
        response.headers['Cache-Control'] = 'max-age=0' # Nécessaire pour IE.

        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = \
                        'attachment;filename="%s"' % filename
        return rrd.exportCSV(host, graphtemplate, ds, start, end, timezone)

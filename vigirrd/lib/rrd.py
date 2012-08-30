# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
################################################################################
#
# RRDGraph Python RRD Graphing library
# Copyright (C) 2007-2012 CS-SI
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
################################################################################
# $Id$

"""
Composant Python pour afficher les données contenues dans des fichiers RRD
"""

import rrdtool
import os
import glob
import time
import calendar
import datetime
import csv
import locale
import copy
import babel, pytz
from cStringIO import StringIO

from logging import getLogger
LOGGER = getLogger(__name__)

from vigilo.common.nx import networkx as nx
from tg import config, request
from pylons.i18n import ugettext as _
from paste.deploy.converters import asbool

from vigilo.common import get_rrd_path

from vigirrd.lib import conffile
from vigirrd.model import DBSession, Host, Graph, PerfDataSource, Cdef
from vigirrd.model.secondary_tables import GRAPH_PERFDATASOURCE_TABLE


def dateToDateObj(date):
    """
    Convertit une date au format "AAAA-MM-JJ" en objet date de Python.

    @param date: Date au format "AAAA-MM-JJ".
    @type date: C{basestring}
    @return: Objet Python pour représenter la date.
    @rtype: C{datetime.datetime}
    """
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    dateobj = datetime.date(year, month, day)
    return dateobj

def dateToTimestamp(date):
    """
    Transforme une date au format "AAAA-MM-JJ" en timestamp UNIX.

    @param date: Date au format "AAAA-MM-JJ".
    @type date: C{basestring}
    @return: Timestamp UNIX équivalent à la date donnée.
    @rtype: C{int}
    """
    return time.mktime(dateToDateObj(date).timetuple())

def listFiles(host):
    """
    List the relevant RRD files for the specified host during the \
    specified time
    """
    files = []
    rrd_base_dir = config['rrd_base']
    rrd_path_mode = config.get("rrd_path_mode", "flat")
    host_path = get_rrd_path(host, base_dir=rrd_base_dir,
                             path_mode=rrd_path_mode)
    rrd_pattern = os.path.join(host_path, '*.rrd')
    LOGGER.debug(rrd_pattern)
    files.extend(glob.glob(rrd_pattern))
    files.sort()
    return files

def getStartTime(host):
    """Returns the timestamp of the first available data for the given host"""
    files = listFiles(host)
    for file_l in files:
        rrd = RRD(file_l)
        try:
            return rrd.getStartTime()
        except RRDError:
            continue
    raise RRDError("Can't find the first timestamp available "
                    "for host %s." % host)

def listDS(files):
    """
    Renvoie la liste des sources de données contenues
    dans une série de fichiers RRD.

    @param files: Liste de fichiers RRD à analyser.
    @type files: C{list} of C{basestring}
    @return: Listes des noms des sources de données disponibles
        en analysant les fichiers RRD indiqués.
    @rtype: C{list} of C{str}
    """
    rrds = map(RRD, files)
    list_l = []
    for rrd in rrds:
        for ds in rrd.listDS():
            if ds in list_l:
                continue
            else:
                list_l.append(ds)
    list_l.sort()
    return list_l

def showMergedRRDs(server, template_name, outfile='-',
        start=0, duration=0, details=1, timezone=0):
    """showMergedRRDs"""
    host = Host.by_name(server)
    if host is None:
        raise RRDNotFoundError, server
    graph = Graph.by_host_and_name(host, template_name)
    if graph is None:
        LOGGER.error("ERROR: The template '%(template)s' does not exist. "
                    "Available templates: %(available)s", {
            'template': template_name,
            'available': ", ".join([g.name for g in host.graphs]),
        })

    # Copie en profondeur pour éviter des écrasements
    # de valeurs entre threads (ticket #549).
    template = copy.deepcopy(conffile.templates[graph.template])
    template["name"] = template_name
    template["vlabel"] = graph.vlabel
    template["last_is_max"] = graph.lastismax
    template["cdefs"] = graph.cdefs
    if graph.min is not None:
        template["min"] = graph.min
    if graph.max is not None:
        template["max"] = graph.max
    ds_map = {}
    ds_list = graph.perfdatasources
    for ds in ds_list:
        ds_map[ds.name] = getEncodedFileName(server, ds.name)
    tmp_rrd = RRD(filename=ds_map, server=server)
    tmp_rrd.graph(template, ds_list, outfile, start=start,
                  duration=duration, details=(int(details)==1),
                  timezone=timezone)

def getEncodedFileName(server, ds):
    """
    Étant donné un nom d'hôte et un indicateur sur cet hôte,
    renvoie le nom du fichier qui contient les informations
    sur cet hôte et cet indicateur.

    @param server: Nom de l'hôte dont les données de métrologie
        nous intéressent.
    @type server: C{basestring}
    @param ds: Nom de l'indicateur qui nous intéresse
        sur l'hôte.
    @type ds: C{basestring}
    @return: Nom du fichier contenant les informations sur
        cet hôte/indicateur.
    @rtype: C{str}
    """
    rrd_base_dir = config['rrd_base']
    rrd_path_mode = config.get("rrd_path_mode", "flat")
    filename = get_rrd_path(server, ds, base_dir=rrd_base_dir,
                            path_mode=rrd_path_mode)
    return filename

# VIGILO_EXIG_VIGILO_PERF_0040:Export des donnees d'un graphe au format CSV
def exportCSV(server, graphtemplate, ds, start, end, timezone):
    """
    export CSV

    # valeurs finales -> dictionnaire
    # - renseigné a partir dictionnaires obtenus pour chaque indicateur
    # - sous la forme :
    #   * cle = indice
    #   * valeur = [TimeStamp, donnee dictionnaire1 pour TimeStamp, ...,
    #                donnee dictionnaireN pour TimeStamp
    @param server : serveur
    @type server : C{str}
    @param graphtemplate : graphe
    @type graphtemplate : C{str}
    @param ds : indicateur graphe
    @type ds : C{str}
    @param start : debut plage export
    @type start : C{str}
    @param end : fin plage export
    @type end : C{str}
    @param timezone : Décalage en minutes du fuseau horaire de l'utilisateur
        (utilisé pour obtenir une représentation textuelle des dates).
    @type timezone : C{int}
    @return : donnees RRD d apres server, indicateur et plage
    @rtype: dictionnaire
    """

    # initialisation
    host = Host.by_name(server)
    graph = Graph.by_host_and_name(host, graphtemplate)
    delta = pytz.FixedOffset(-timezone)

    # Si l'indicateur est All ou n'existe pas pour cet hôte,
    # tous les indicateurs sont pris en compte.
    if not ds or ds.lower() == "all":
        ds_list = [pds.name.encode('utf-8') for pds in graph.perfdatasources]
    elif isinstance(ds, unicode):
        ds_list = [ds.encode('utf-8')]
    else:
        ds_list = [str(ds)]

    ds_map = {}
    for ds in ds_list:
        ds_map[ds] = getEncodedFileName(server, ds)

    headers = ['Timestamp', 'Date']
    headers.extend(ds_list)

    # Construction d'une liste de listes contenant un horodatage
    # et les valeurs des différents indicateurs sélectionnés.
    # L'horodatage arrive toujours en premier. Ensuite, les valeurs
    # arrivent dans l'ordre des indicateurs donnés dans ds_list.
    result = []
    format_date = config.get('csv_date_format', "long")
    format_value = asbool(config.get('csv_respect_locale', False))
    date_locale = 'en_US'

    # Au cas où la configuration serait changée dynamiquement.
    if not format_value:
        locale.setlocale(locale.LC_NUMERIC, 'C')
        locale.setlocale(locale.LC_TIME, 'C')
    else:
        try:
            lang = request.accept_language.best_matches()
        except TypeError:
            # Lorsque le thread n'a pas de "request" associée
            # (ex: dans les tests unitaires), TypeError est levée.
            lang = []

        for tentative_lang in lang:
            try:
                tentative_lang = tentative_lang.replace('-', '_')
                # Pour le formattage des nombres.
                locale.setlocale(locale.LC_NUMERIC, tentative_lang)
                # Pour le formattage des dates/heures.
                locale.setlocale(locale.LC_TIME, tentative_lang)
            except locale.Error:
                pass
            else:
                LOGGER.debug(u"Preparing to format CSV values, "
                            "using locale %r" % tentative_lang)
                date_locale = tentative_lang
                break

    for ds in ds_list:
        tmp_rrd = RRD(filename=ds_map[ds], server=server)
        # Récupère les données de l'indicateur sous la forme suivante :
        # dict(timestamp1=[valeur1], timestamp2=[valeur2], ...)
        # Les valeurs sont des listes car un fichier peut potentiellement
        # contenir plusieurs indicateurs. Ce n'est pas le cas sur Vigilo
        # où la liste de valeurs contiendra TOUJOURS une seule valeur.
        values_ind = tmp_rrd.fetchData(
            ds_names=['DS'], start_a=start, end_a=end)

        for index, timestamp in enumerate(values_ind):
            # Si l'index n'existe pas encore dans le résultat,
            # c'est qu'il s'agit du premier indicateur que l'on traite.
            # On ajoute donc le timestamp à la liste avant tout.
            if len(result) <= index:
                # Le timestamp est ajouté, une première fois sous forme
                # d'horodatage UNIX à destination de scripts et une seconde
                # fois sous forme textuelle à destination des exploitants.

                # 1. On convertit le timestamp depuis UTC vers le fuseau
                #    horaire donné par le navigateur de l'utilisateur.
                date = pytz.utc.localize(datetime.datetime.utcfromtimestamp(
                            timestamp)).astimezone(delta)
                # 2. On utilise la représentation des dates/heures issue
                #    de la locale de l'utilisateur (ou "en_US" par défaut).
                date = babel.dates.format_datetime(date, format_date,
                            locale=date_locale)
                result.append([timestamp, date])

            # On prépare le format adéquat en fonction du type de la valeur.
            # Le formattage tiendra compte de la locale.
            # Exemples pour le français :
            #   int(1234) -> "1 234"
            #   float(1234.56) -> "1234,56"
            format_for_value = isinstance(values_ind[timestamp][0], int) and \
                '%d' or '%f'
            value = (values_ind[timestamp][0] is not None) and \
                locale.format(format_for_value, values_ind[timestamp][0]) or \
                None
            result[index].append(value)

    # On trie les valeurs par horodatage ascendant.
    result = sorted(result, key=lambda r: int(r[0]))

    # Écriture de l'en-tête, puis des données dans un buffer.
    # Le contenu final du buffer correspond au fichier CSV exporté.
    buf = StringIO()
    csv_writer = csv.writer(buf,
        delimiter=config.get("csv_delimiter_char", ';'),
        escapechar=config.get("csv_escape_char", '\\'),
        quotechar=config.get("csv_quote_char", '"'),
        quoting=csv.QUOTE_ALL)

    csv_writer.writerow(headers)
    csv_writer.writerows(result)
    return buf.getvalue()

def getExportFileName(host, ds_graph, start, end, timezone):
    """
    Determination nom fichier pour export
    -> <hote>_<ds_graph>_<date_heure_debut>_<date_heure_fin>
    avec format <date_heure_...> = AAMMJJ-hhmmss

    @param host : hôte
    @type host : C{str}
    @param ds_graph : indicateur graphe (nom du graphe ou d'un des indicateurs)
    @type ds_graph : C{str}
    @param start : date-heure de debut des donnees
    @type start : C{str}
    @param end : duree des donnees
    @type end : C{str}
    @param timezone: décalage en minutes entre l'heure UTC
        et l'heure dans le fuseau horaire de l'utilisateur
        (p.ex. 60 = UTC+01).
    @type timezone: C{int}

    @return: nom du fichier
    @rtype: C{str}
    """

    # plage temps sous forme texte
    format = '%Y/%m/%d-%H:%M:%S'
    delta = pytz.FixedOffset(-timezone)

    dt = pytz.utc.localize(datetime.datetime.utcfromtimestamp(
                            int(start))).astimezone(delta)
    str_start = dt.strftime(format)

    dt = pytz.utc.localize(datetime.datetime.utcfromtimestamp(
                            int(end))).astimezone(delta)
    str_end = dt.strftime(format)

    host = host.encode('utf-8', 'replace')
    ds_graph = ds_graph.encode('utf-8', 'replace')

    # nom fichier
    filename = '%s - %s (%s - %s)' % (host, ds_graph, str_start, str_end)
    filename = filename.encode('backslash')

    # extension
    filename += ".csv"

    return filename


class RRDError(Exception):
    pass
class RRDNoDSError(RRDError):
    pass
class RRDNotFoundError(RRDError):
    pass

class RRD(object):
    """An RRD database"""

    def __init__(self, filename=None, server=None):
        self.ds = []
        self.filename = filename
        self.server = server
        if server is not None:
            self.host = Host.by_name(server)

    def getGraphs(self):
        """Gets templated graphes"""
        return self.host.graphs

    def getStep(self):
        """Get step from the RRD"""
        return rrdtool.info(self.filename)["step"]

    def getLast(self):
        """getLast"""
        return rrdtool.last(str(self.filename))

    def getPeriodCF(self, start):
        """
        Retourne la fonction de calcul à appliquer
        pour la période commençant à la date donnée.

        @param start: Date de début de la période considérée.
        @type start: C{int}
        @return: Fonction de calcul à utiliser ("LAST" ou "AVERAGE").
        @rtype: C{str}
        """
        infos = rrdtool.info(self.filename)
        step = infos['step']
        now = time.mktime(datetime.datetime.utcnow().timetuple())
        i = 0
        rras = []
        while ('rra[%d].cf' % i) in infos:
            # Date de la 1ère valeur possible dans ce RRA.
            first = now - infos['rra[%d].rows' % i] * step
            # Si la date demandée n'appartient pas
            # à ce RRA, on l'ignore.
            if start < first:
                i += 1
                continue

            rras.append({
                'cf': infos['rra[%d].cf' % i],
                'first': first,
            })
            i += 1
        # On trie les RRA restants par granularité décroissante.
        rras.sort(cmp=lambda a, b: int(b['first'] - a['first']))
        if not rras:
            return "AVERAGE"
        return rras[0]['cf']

    def getStartTime(self):
        """Gets the timestamp of the first non-null entry in the RRD"""
        first =  rrdtool.first(self.filename)
        end = rrdtool.last(self.filename)
        cf = self.getPeriodCF(first)
        try:
            info , _ds_rrd , data = rrdtool.fetch(self.filename,
                    cf, "--start", str(first), "--end", str(end))
        except rrdtool.error:
            # Adjust for daylight saving times
            first = first - 3600
            end = end + 3600
            info , _ds_rrd , data = rrdtool.fetch(self.filename,
                    cf, "--start", str(first), "--end", str(end))
        #start_rrd = info[0]
        #end_rrd = info[1]
        step = info[2]
        for line in data:
            all_none = True
            for value in line:
                if value is not None:
                    all_none = False
            if not all_none:
                break
            first = first + step
        if first >= end:
            raise RRDError("The RRD file looks empty !")
        return first

    def getStartTimePath(self):
        """Returns the start timestamp of the RRD, based on its path.
           It is not necessarily the timestamp of the first entry.
           Unused at the moment."""
        dir_l = os.path.dirname(self.filename)
        hour = os.path.basename(dir_l).rstrip('Z')
        day = os.path.basename(os.path.dirname(dir_l))
        t_tuple = time.strptime("%s %s:00:00 UTC"%(day, hour), \
        "%Y-%m-%d %H:%M:%S %Z")
        t_stamp = calendar.timegm(t_tuple)
        start = t_stamp - 1
        return start

    def fetchData(self, ds_names, start_a=None, end_a=None):
        """
        Gets the data in the RRD, for the specified DataSources,
        for the optional timeslot
        """
        if not os.path.exists(self.filename):
            raise RRDNotFoundError(self.filename)

        res = {}
        if start_a is None:
            try:
                start = self.getStartTime() - 1
            except RRDError:
                # RRD is empty
                return res
        else:
            start = int(start_a)

        now = int(time.time())
        if start >= now:
            # No data yet
            LOGGER.debug("No data yet")
            return res

        if end_a is not None:
            end = int(end_a)
        else:
            # one hour plus one second, start should be 1 sec in the past
            end = start + 3600 + 1

        if end > now:
            LOGGER.debug("truncating %(filename)s to %(now)d "
                "instead of %(end)d", {
                    'filename': self.filename,
                    'now': now,
                    'end': end,
                })
            end = now
        cf = self.getPeriodCF(start)
        LOGGER.debug("rrdtool fetch %s %s --start %s --end %s" %
                    (self.filename, cf, str(start), str(end)))

        info , ds_rrd , data = rrdtool.fetch(str(self.filename), cf,
                                   "--start", str(start), "--end", str(end))
        #start_rrd = info[0]
        #end_rrd = info[1]
        step = info[2]

        # put the mapping of indexes in the rrd to their place in the final list
        ds_mapping = {}
        for i in range(len(ds_rrd)):
            ds = ds_rrd[i]
            if ds in ds_names:
                ds_mapping[i] = ds_names.index(ds)

        # Create the data dict
        tstamp = start + 1
        for line in data:
            # fill with 'None', len(ds_names) times
            values = [ None for i in ds_names ]
            for i in range(len(line)):
                # we have a mapping for it, so store it
                if ds_mapping.has_key(i):
                    values[ds_mapping[i]] = line[i]
            res[tstamp] = values
            tstamp = tstamp + step
            if tstamp > end - step:
                break

        return res

    def update(self, ds_list, data):
        """Updates the given ds in the RRD with the given values"""
        timestamps = data.keys()
        timestamps.sort()
        LOGGER.debug("feeding data...")
        for timestamp in timestamps:
            values = data[timestamp]
            clean_values = []
            for v in values:
                if v is None:
                    clean_values.append("U")
                else:
                    clean_values.append(str(v))
            args = [self.filename, "-t", ":".join(ds_list)]
            args.append("%s@%s" % (timestamp, ":".join(clean_values)))
            try:
                rrdtool.update(*args)
            except rrdtool.error:
                # Daylight savings
                LOGGER.info("Skipped daylight savings (timestamp = %s)",
                            timestamp)
                continue

    def graph(self, template, ds_list, outfile="-", format='PNG',
              start=0, duration=0, details=True, lazy=True, timezone=0):
        """
        Génère un graphe pour le RRD et les paramètres demandés.

        @param template: modèle graphique de génération, pris dans le fichier
            de configuration template.py et complété avec les valeurs trouvées
            en base de données (voir fonction L{showMergedRRDs}).
        @type  template: C{dict}
        @param ds_list: liste d'objets PerfDataSource à grapher.
        @type  ds_list: C{list}
        @param outfile: chemin du fichier où générer le graphe
        @type  outfile: C{str}
        @param format: format d'image, doit être géré par rrdtool
        @type  format: C{str}
        @param start: timestamp de début du graphe
        @type  start: C{int}
        @oaram duration: durée représentée
        @type  duration: C{int}
        @param details: affichage du titre et de la légende
        @type  details: C{bool}
        @param lazy: voir le paramètre C{lazy} de rrdtool
        @type  lazy: C{bool}
        @param timezone: décalage en minutes entre l'heure UTC
            et l'heure dans le fuseau horaire de l'utilisateur
            (p.ex. 60 = UTC+01).
        @type timezone: C{int}
        """
        if outfile != "-":
            imgdir = os.path.dirname(outfile)
            if not os.path.exists(imgdir):
                os.makedirs(imgdir)

        # La variable TZ utilise la convention POSIX
        # (ie. la direction du temps est inversée).
        if timezone < 0:
            # Python suit la définition mathématique de la division
            # euclidienne et du modulo, ce qui ne nous arrange pas ici.
            tz_hours = (-timezone) / 60
            tz_mins  = (-timezone) % 60
        else:
            tz_hours = -(timezone / 60)
            tz_mins  = -(timezone % 60)

        # On positionne TZ à un fuseau horaire
        # du type "UTC-01" ou encore "UTC+09:30".
        # Cette variable permet change l'interprétation des horodatages
        # donnés en entrée pour que rrdtool ajuste les dates/heures.
        # Méthode non thread-safe, mais c'est la seule reconnue par rrdtool.
        old_tz = os.environ.get('TZ')
        os.environ['TZ'] = 'UTC%+03d%s' % (
            tz_hours,
            tz_mins and (":%02d" % tz_mins) or ""
        )

        # On choisit la langue qui sera utilisée pour le rendu.
        try:
            lang = request.accept_language.best_matches()
        except TypeError:
            # Lorsque le thread n'a pas de "request" associée
            # (ex: dans les tests unitaires), TypeError est levée.
            lang = None

        if lang:
            selected_locale = lang[0].replace('-', '_')
            if "_" not in selected_locale:
                selected_locale = "%s_%s" % (selected_locale,
                                             selected_locale.upper())
            # On force l'utilisation d'une locale UTF-8 pour rrdtool.
            # Cf. http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=493553
            selected_locale += '.utf8'
            LOGGER.debug(u"Trying to set rrdtool's locale to %s" %
                selected_locale)

            # On supprime les variables d'environnement susceptibles d'avoir
            # la priorité sur LC_TIME lors du choix de la locale.
            for env_var in ('LC_ALL', 'LANGUAGE', 'LANG'):
                if env_var in os.environ:
                    del os.environ[env_var]

            # On doit manipuler à la fois os.environ et setlocale()
            # pour changer la locale du processus courant mais aussi
            # celle des sous-processus qu'il crée.
            try:
                locale.setlocale(locale.LC_TIME, selected_locale)
                os.environ['LC_TIME'] = selected_locale
            except locale.Error:
                pass # locale non supportée, c'est pas grave

        start_i = int(start)
        if start_i == 0:
            start_i = int((int(time.time())) - 24*3600 - 1)

        duration_i = int(duration)
        if duration_i == 0:
            end_i = int(time.time())
        else:
            end_i = int(start_i + duration_i)
        # Compute the x-axis labels
        duration_i = end_i - start_i

        #if duration_i <= 7 * 3600:
        #    xgrid = "MINUTE:30:HOUR:1:HOUR:1:0:%d/%m %Hh"
        #elif duration_i > 7 * 3600 and duration_i <= 25 * 3600:
        #    xgrid = "HOUR:1:HOUR:6:HOUR:6:0:%d/%m %Hh"
        #elif duration_i > 25 * 3600 and duration_i <= 8 * 24 * 3600:
        #    xgrid = "HOUR:6:DAY:1:DAY:1:0:%d/%m"
        #elif duration_i > 8 * 24 * 3600 and duration_i <= 15 * 24 * 3600:
        #    xgrid = "DAY:1:DAY:2:DAY:2:0:%d/%m"
        #elif duration_i > 15 * 24 * 3600 and duration_i <= 4 * 31  * 24 * 3600:
        #    xgrid = "DAY:5:DAY:10:DAY:10:0:%d/%m"
        #else:
        #    xgrid = "WEEK:2:MONTH:1:MONTH:1:0:%b"
        a = [
                str(outfile),
                #"--step", str(step),
                #"--x-grid", xgrid,
                "--start", str(start_i),
                "--end", str(end_i),
                "--imgformat", format,
        ]
        if "min" in template:
            a.extend(["-l", str(template["min"])])
        if "max" in template:
            a.extend(["-u", str(template["max"])])
        if "options" in template:
            for option in template["options"]:
                a.append(option)

        a.append("--title")
        if not details:
            a.append(template["name"])
            a.append("--no-legend")
#            a.append("--only-graph")
            a.append("--width")
            a.append(250)
            a.append("--height")
            a.append(64)
        else:
            if len(self.server) > 35:
                ellipsis_server = self.server[:15] + '(...)' + \
                                    self.server[-15:]
            else:
                ellipsis_server = self.server
            a.append("%s: %s" % (ellipsis_server, template["name"]))
            a.append("--width")
            a.append(self.host.width)
            a.append("--height")
            a.append(self.host.height)
            a.append("--vertical-label")
            a.append(template["vlabel"])
            a.append("TEXTALIGN:left")
        if lazy:
            a.append("--lazy")
        # Curve smoothing
        a.append("-E")

        # Calcul du label le plus long
        labels = []
        for d in ds_list:
            label = d.label
            if not label:
                label = d.name
            labels.append(len(label))
        justify = max(labels)

        # Ajoute la date de début et de fin avant la légende, centrées.
        # Le format par défaut est celui le plus adapté à la locale.
        format_date = config.get(
                'graph_date_format',
                locale.nl_langinfo(locale.D_T_FMT)
            ).encode('utf-8')

        # Le caractère ":" est réservé dans rrdtool et doit être échappé.
        # Le rstrip() permet de supprimer un espace présent en trop à la fin
        # du texte, lié à l'absence de fuseau horaire et à la présence du
        # format %Z par défaut dans la plupart des locales.
        start_date = datetime.datetime.fromtimestamp(
            start_i).strftime(format_date).replace(':', '\\:').rstrip()
        end_date = datetime.datetime.fromtimestamp(
            end_i).strftime(format_date).replace(':', '\\:').rstrip()
        a.append(
            (
                'COMMENT:' + (_('From "%(start)s" to "%(end)s"') % {
                    'start': start_date.decode('utf-8'),
                    'end': end_date.decode('utf-8'),
                }) + '\\c'
            ).encode('utf-8')
        )
        a.append("COMMENT:  \\n")

        # Tabs (legend)
        s = "COMMENT:%s" % (" " * (justify + 1))
        for tab in template["tabs"]:
            # if we have a nicer label, use it
            if tab in config.static_labels:
                tabstr = config.static_labels[tab]
            else:
                # if we dont, too bad, just print it.
                tabstr = tab
            s += " "*7 + tabstr.strip() # align it

        a.append(str(s)+"\\n")

        defs = []
        for i in range(len(ds_list)):
            defs.extend(self.get_def(ds_list, i, template, start))
        try:
            defs = self._sort_defs(defs, ds_list)
        except nx.NetworkXUnfeasible, e:
            try:
                error_message = unicode(e)
            except UnicodeDecodeError:
                error_message = unicode(str(e), 'utf-8', 'replace')
            LOGGER.error(_("Can't sort DS dependencies"))
        a.extend(defs)

        for i, d in enumerate(ds_list):
            if "last_is_max" in template and template["last_is_max"] \
                    and i == len(ds_list)-1:
                is_max = True
            else:
                is_max = False
            a.extend(self.get_graph_cmd_for_ds(d, i, template, is_max, justify))

        # rrdtool.graph() ne sait manipuler que le type <str>.
        a = [isinstance(e, unicode) and e.encode('utf-8') or str(e) for e in a]
        LOGGER.debug("rrdtool graph '%s'" % "' '".join(a))

        rrdtool.graph(*a)
        # Restaure la valeur précédente de TZ
        # (non thread-safe, mais évite de trop polluer Python).
        if old_tz is None:
            del os.environ['TZ']
        else:
            os.environ['TZ'] = old_tz

    def _sort_defs(self, defs, ds_list):
        """
        Tri des définitions (DEF et CDEF) en fonction de leur dépendance les
        unes sur les autres.

        @param defs: définitions de variable (syntaxe rrdtool)
        @type  defs: C{list}
        @param ds_list: liste complète d'objets PerfDataSource à afficher sur
            le graphe
        @type  ds_list: C{list}
        @rtype: C{list}
        """
        graph = nx.DiGraph()
        for d in defs:
            ctype = d.split(":")[0]
            name = d.split(":")[1].split("=")[0]
            graph.add_node(name, d=d)
            if ctype == "CDEF":
                formula = d.split(":")[1].split("=")[1]
                for cmd in formula.split(","):
                    if not cmd.startswith("data_"):
                        continue
                    graph.add_edge(name, cmd)
        nodes = nx.algorithms.dag.topological_sort(graph)
        if nodes is None: # compatibilité networkx < 1.3
            # message non traduit pour être aussi compatible que possible
            raise nx.NetworkXUnfeasible("Graph contains a cycle.")
        nodes.reverse()
        return [ graph.node[n]["d"] for n in nodes ]

    def get_params(self, i, template, is_max=False):
        """
        Retourne les paramètres graphiques pour la PDS à l'index L{i}, en
        fonction du modèle et du paramètre.

        @param i: index courant dans L{ds_list}
        @type  i: C{int}
        @param template: modèle graphique de génération, transmis par la
            fonction L{graph}
        @type  template: C{dict}
        @param is_max: traiter cette PDS comme la limite maximum du graphe
        @type  is_max: C{bool}
        @rtype: C{dict}

        """
        if is_max:
            # C'est le max, on fait juste un trait noir
            params = { "type": "LINE1", "color": "#000000", "stack": False }
        else:
            # If we know how to graph the n-th DS...
            if i < len(template["draw"]):
                # ...use those params...
                params = template["draw"][i]
            else:
                # ...else just use the first params.
                params = template["draw"][0]
        return params

    def get_def(self, ds_list, i, template, start):
        """
        Génère un indicateur consolidé "<ds>_orig" correspondant
        à la valeur moyenne ou à la dernière valeur sur la période
        et le pas considérés.

        @param ds_list: liste complète d'objets PerfDataSource à afficher sur
            le graphe
        @type  ds_list: C{list}
        @param i: index courant dans L{ds_list}
        @type  i: C{int}
        @param template: modèle graphique de génération, transmis par la
            fonction L{graph}
        @type  template: C{dict}
        @param start: Horodatage du début de la période représentée.
        @type  start: C{int}
        """
        cdef = [ c for c in template["cdefs"] if c.name == ds_list[i].name ]
        if cdef:
            cmds = self.get_cdef(cdef[0], ds_list, i, start)
        else:
            cmds = self.get_ds_def(ds_list, i, start)

        # Remplace l'indicateur "<ds>" par la valeur de "<ds>_orig"
        # générée précédemment, en lui appliquant le facteur approprié.
        factor = 1
        params = self.get_params(i, template)
        if params.has_key("invert") and params["invert"]:
            factor = -1
        if ds_list[i].factor != 1:
            factor = factor * ds_list[i].factor
        cmds.append("CDEF:data_%s=data_%s_orig,%1.10f,*" % (i, i, factor))

        return cmds

    def get_cdef(self, cdef, ds_list, i, start):
        """
        Retourne la partie de la commande RRD concernant la définition des
        valeurs à grapher (CDEFs, et valeurs après application du facteur
        défini dans la conf).

        @param cdef: objet Cdef à considérer
        @type  cdef: L{Cdef}
        @param ds_list: liste complète d'objets PerfDataSource à afficher sur
            le graphe
        @type  ds_list: C{list}
        @param i: index courant dans L{ds_list}
        @type  i: C{int}
        """
        result = []
        cmd_list = cdef.cdef.split(",")
        for cmd_index, cmd in enumerate(cmd_list):
            if len(cmd) == 1:
                continue # c'est un opérateur
            ds_names = [ ds.name for ds in ds_list ]
            if cmd in ds_names:
                cmd_list[cmd_index] = "data_%d" % ds_names.index(cmd)
            else: # c'est un autre RRD, pas sur ce graphe
                rrd_path_mode = config.get("rrd_path_mode", "flat")
                rrdfile = get_rrd_path(self.server, cmd,
                                       base_dir=config['rrd_base'],
                                       path_mode=rrd_path_mode)
                cf = RRD(rrdfile).getPeriodCF(start)
                result.append("DEF:data_%s_source=%s:DS:%s" %
                              (i, rrdfile, cf))
                cmd_list[cmd_index] = "data_%d_source" % i
        result.append("CDEF:data_%s_orig=%s" % (i, ",".join(cmd_list)))
        return result

    def get_ds_def(self, ds_list, i, start):
        """
        Retourne la partie de la commande RRD concernant la définition des
        fichiers RRD source.

        @param ds_list: liste complète d'objets PerfDataSource à afficher sur
            le graphe
        @type  ds_list: C{list}
        @param i: index courant dans L{ds_list}
        @type  i: C{int}
        @rtype: C{list}
        """
        if isinstance(self.filename, dict):
            rrdfile = self.filename[ds_list[i].name]
        else:
            rrdfile = self.filename
        if not os.path.exists(rrdfile):
            raise RRDNotFoundError(rrdfile)
        cf = RRD(rrdfile).getPeriodCF(start)
        return [ "DEF:data_%s_orig=%s:DS:%s" % (i, rrdfile, cf) ]

    def get_graph_cmd_for_ds(self, d, i, template, is_max=False, justify=18):
        """
        Retourne la partie de la commande RRD concernant la génération du
        graphe.

        @param d: objet PerfDataSource à considérer
        @type  d: L{PerfDataSource}
        @param i: index courant dans L{ds_list}
        @type  i: C{int}
        @param template: modèle graphique de génération, transmis par la
            fonction L{graph}
        @type  template: C{dict}
        @param is_max: traiter cette PDS comme la limite maximum du graphe
        @type  is_max: C{bool}
        @param justify: nombre de caractères pour la justification de la
            légende
        @type  justify: C{int}
        @rtype: C{list}
        """
        cmd = []

        params = self.get_params(i, template, is_max)
        # If we have a nicer label, use it
        label = d.label
        if not label:
            label = d.name

        graphline = "%s:data_%s%s:%s" % (params["type"], i, params["color"], \
            label.replace('\\', '\\\\').replace(':', '\\:').ljust(justify))
#            LOGGER.debug("params=%s, has_key=%d" %
#                (params, params.has_key("stack")))
        if params.has_key("stack") and params["stack"]:
            graphline += ":STACK"
#                LOGGER.debug("added + :STACK to %s"%graphline)
        cmd.append(graphline)
        if is_max:
            cmd.append("GPRINT:data_%s:LAST:%s\\n" % (i, "%7.2lf%s"))
        else:
            for tab in template["tabs"]:
                cmd.append("GPRINT:data_%s:%s:%s" % (i, tab, "%7.2lf%s"))
            cmd[-1] = cmd[-1] + "\\n"
        return cmd

    def getLastValue(self, ds):
        """
        Lecture derniere valeur RRD
        @return: Dernière valeur.
        @rtype: C{str} ou C{None}
        """
        # dernier timestamp et step
        lasttime = self.getLast()
        step = self.getStep()
        if not lasttime or not step:
            return None

        # bornes selon timestamp et step
        start = lasttime - step
        end = lasttime

        # informations
        cf = self.getPeriodCF(start)
        _info, _ds_rrd, data = rrdtool.fetch(self.filename, cf,
                               "--start", str(start), "--end", str(end))

        if len(data) == 0 or len(data[0]) == 0:
            return None

        lastValue = data[0][0]
        if lastValue is None:
            return None

        factor = DBSession.query(
                PerfDataSource.factor
            ).join(
                (GRAPH_PERFDATASOURCE_TABLE,
                    GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource ==
                    PerfDataSource.idperfdatasource),
                (Graph, Graph.idgraph == GRAPH_PERFDATASOURCE_TABLE.c.idgraph),
            ).filter(PerfDataSource.name == unicode(ds)
            ).filter(Graph.idhost == self.host.idhost
            ).scalar()
        if factor is None:
            factor = 1
        return lastValue * factor

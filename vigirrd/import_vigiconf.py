# -*- coding: utf-8 -*-
"""Setup the vigirrd application"""

import os
import stat
import logging
logging.basicConfig(level=logging.DEBUG)

import transaction
from tg import config
from paste.deploy import appconfig

from vigirrd.config.environment import load_environment
from vigirrd import model

LOGGER = logging.getLogger(__name__)


def import_vigiconf(conf_file):
    LOGGER.info("Loading the configuration")
    # Chargement de la configuration de VigiRRD
    conf = appconfig("config:%s#main" % conf_file)
    load_environment(conf.global_conf, conf.local_conf)
    # Chargement du schéma de la base
    LOGGER.debug("Re-creating tables")
    engine = config['pylons.app_globals'].sa_engine
    model.metadata.drop_all(bind=engine)
    model.metadata.create_all(bind=engine)
    # Chargement du fichier venant de VigiConf
    load_vigiconf_file()
    transaction.commit()
    # Permissions
    sqlite_filename = config["sqlalchemy.url"]
    if sqlite_filename.startswith("sqlite:///"):
        sqlite_filename = sqlite_filename[10:]
        chmod_644(sqlite_filename)
    LOGGER.debug("Successfully loaded")

def load_vigiconf_file():
    vigiconf_data = {"hostscfg": {}, "labels": {}}
    execfile(config["vigiconf_file"], vigiconf_data)
    LOGGER.debug("Inserting data (%d hosts)", len(vigiconf_data["hostscfg"]))
    for hostname, hostdata in vigiconf_data["hostscfg"].iteritems():
        h = model.Host(name=unicode(hostname),
                       grid=unicode(hostdata["grid"]),
                       height=hostdata["height"],
                       width=hostdata["width"],
                       step=hostdata["step"],
                      )
        model.DBSession.add(h)

        for graphname, graphdata in hostdata["graphes"].iteritems():
            g = model.Graph(name=unicode(graphname),
                            template=unicode(graphdata["template"]),
                            vlabel=unicode(graphdata["vlabel"]),
                            host=h)
            if "last_is_max" in graphdata:
                g.lastismax = graphdata["last_is_max"]
            model.DBSession.add(g)

            for dsname in graphdata["ds"]:
                ds = model.PerfDataSource.by_name(dsname)
                if not ds:
                    ds = model.PerfDataSource(name=unicode(dsname))
                    if dsname in vigiconf_data["labels"]:
                        ds.label = unicode(vigiconf_data["labels"][dsname])
                    if dsname in graphdata["factors"]:
                        ds.factor = graphdata["factors"][dsname]
                    if "max_values" in graphdata and \
                            dsname in graphdata["max_values"]:
                        ds.max = graphdata["max_values"][dsname]
                    model.DBSession.add(ds)
                g.perfdatasources.append(ds)

        model.DBSession.flush()

def chmod_644(filename):
    os.chmod(filename, # chmod 644
             stat.S_IRUSR | stat.S_IWUSR | \
             stat.S_IRGRP | stat.S_IROTH )

def main():
    conf_file = os.getenv("VIGILO_SETTINGS", "/etc/vigilo/vigirrd/settings.ini")
    import_vigiconf(conf_file)

if __name__ == "__main__":
    main()

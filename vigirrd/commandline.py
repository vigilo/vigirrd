# -*- coding: utf-8 -*-
# Copyright (C) 2006-2015 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Setup the vigirrd application"""

import os
import imp
import time
import logging
import logging.config

from tg import config
from paste.deploy import appconfig

CACHE_KEEP_MINUTES = 5
LOGGER = logging.getLogger(__name__)


def load_conf():
    conf_file = os.getenv("VIGILO_SETTINGS",
                          "/etc/vigilo/vigirrd/settings.ini")
    logging.config.fileConfig(conf_file)
    LOGGER.debug("Loading the configuration")
    # Chargement de la configuration de VigiRRD
    conf = appconfig("config:%s#main" % conf_file)

    # Chargement du fichier "app_cfg.py" se trouvant à côté de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ conf.global_conf['here'] ])
    app_cfg = imp.load_module('vigirrd.config.app_cfg', *mod_info)

    # Initialisation de l'environnement d'exécution.
    load_environment = app_cfg.base_config.make_load_environment()
    load_environment(conf.global_conf, conf.local_conf)


def cleanup_cache():
    """
    Nettoyage du cache des images, à mettre dans cron.
    Cette fonction est exportée en exécutable par un point d'entrée.
    """
    load_conf()
    cache_dir = config["image_cache_dir"]
    if not os.path.exists(cache_dir):
        return
    limit = int(time.time()) - CACHE_KEEP_MINUTES * 60
    for img in os.listdir(cache_dir):
        if not img.endswith(".png"):
            continue
        img_path = os.path.join(cache_dir, img)
        img_ts = os.stat(img_path).st_mtime
        if img_ts >= limit:
            continue
        LOGGER.debug("Removing %s" % img_path)
        os.remove(img_path)



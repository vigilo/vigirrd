# -*- coding: utf-8 -*-
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Setup the vigirrd application"""

import os
import time
import logging
logging.basicConfig(level=logging.DEBUG)

from tg import config
from paste.deploy import appconfig

from vigirrd.config.environment import load_environment

CACHE_KEEP_MINUTES = 5
LOGGER = logging.getLogger(__name__)


def load_conf():
    LOGGER.info("Loading the configuration")
    conf_file = os.getenv("VIGILO_SETTINGS",
                          "/etc/vigilo/vigirrd/settings.ini")
    # Chargement de la configuration de VigiRRD
    conf = appconfig("config:%s#main" % conf_file)
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



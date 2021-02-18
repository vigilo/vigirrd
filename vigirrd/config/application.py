# -*- coding: utf-8 -*-
# Copyright (C) 2006-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""WSGI middleware initialization for the vigirrd application."""

import imp
import os.path
from pkg_resources import resource_filename
from tg.support.statics import StaticsMiddleware

import tg

__all__ = ['make_app']


def make_app(global_conf, **app_conf):
    """
    Set vigirrd up with the settings found in the configuration file used.

    This is the PasteDeploy factory for the vigirrd application.

    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.

    @param global_conf: The global settings for vigirrd (those
        defined under the ``[DEFAULT]`` section).
    @type global_conf: dict
    @return: The vigirrd application with all the relevant middleware
        loaded.
    """
    # Charge le fichier "app_cfg.py" se trouvant aux côtés de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ global_conf['here'] ])
    app_cfg = imp.load_module('vigirrd.config.app_cfg', *mod_info)
    base_config = app_cfg.base_config

    # Initialisation de l'application et de son environnement d'exécution.
    app = base_config.make_wsgi_app(global_conf, app_conf, wrap_app=None)

    max_age = app_conf.get("cache_max_age")
    try:
        max_age = int(max_age)
    except (ValueError, TypeError):
        max_age = 0

    app = StaticsMiddleware(app, app_conf["image_cache_dir"], max_age)
    return app

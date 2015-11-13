# -*- coding: utf-8 -*-
# Copyright (C) 2006-2015 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""WSGI middleware initialization for the vigirrd application."""

import imp
import os.path
from pkg_resources import resource_filename
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser

import tg

__all__ = ['make_app']


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set vigirrd up with the settings found in the PasteDeploy configuration
    file used.

    This is the PasteDeploy factory for the vigirrd application.

    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.

    @param global_conf: The global settings for vigirrd (those
        defined under the ``[DEFAULT]`` section).
    @type global_conf: dict
    @param full_stack: Should the whole TG2 stack be set up?
    @type full_stack: str or bool
    @return: The vigirrd application with all the relevant middleware
        loaded.
    """
    # Charge le fichier "app_cfg.py" se trouvant aux côtés de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ global_conf['here'] ])
    app_cfg = imp.load_module('vigirrd.config.app_cfg', *mod_info)
    base_config = app_cfg.base_config

    # Initialisation de l'application et de son environnement d'exécution.
    load_environment = base_config.make_load_environment()
    make_base_app = base_config.setup_tg_wsgi_app(load_environment)
    app = make_base_app(global_conf, full_stack=True, **app_conf)

    max_age = app_conf.get("cache_max_age")
    try:
        max_age = int(max_age)
    except (ValueError, TypeError):
        max_age = None

    image_cache = StaticURLParser(tg.config["image_cache_dir"],
                                  cache_max_age=max_age)

    app = Cascade([image_cache, app])
    return app

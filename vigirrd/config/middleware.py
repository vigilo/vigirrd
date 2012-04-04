# -*- coding: utf-8 -*-
# Copyright (C) 2006-2012 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""WSGI middleware initialization for the vigirrd application."""

from vigirrd.config.app_cfg import base_config
from vigirrd.config.environment import load_environment
import tg

from pkg_resources import resource_filename
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory.
# make_base_app will wrap the TG2 app with all the middleware it needs.
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


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
    app = make_base_app(global_conf, full_stack=full_stack, **app_conf)

    image_cache = StaticURLParser(tg.config["image_cache_dir"])

    app = Cascade([image_cache, app])
    return app

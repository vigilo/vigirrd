# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
# Copyright (C) 2007-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Configuration for RRDGraph basée sur des fichiers de conf.

Le fonctionnement est inspiré du module de configuration de Django.
"""

import os
import UserDict
from logging import getLogger
LOGGER = getLogger(__name__)

from tg import config

ALLOWED_KEYS = ("templates", )
MTIMES = {}

__all__ = ("reload", "templates")


class Settings(UserDict.DictMixin, object):
    """
    A read-only dictionary that allows access only to selected settings.

    Use the L{load_file()} method to populate the dict.

    @ivar filename: Filename to load, defaults to "settings.py"
    @type filename: C{str}
    @ivar conf_file: The path of the chosen file (used for logging)
    @type conf_file: C{str}
    """

    def __init__(self):
        self.__dct = {}
        self.conf_file = None

    def __getitem__(self, name):
        if name not in ALLOWED_KEYS:
            raise ValueError('Invalid name', name)
        return self.__dct[name]

    def keys(self):
        return [k for k in self.__dct if k in ALLOWED_KEYS]

    def empty(self):
        self.__dct = {}

    def load_file(self, filename):
        """
        Load a specific file

        @param filename: the file path to load. Must exist and be valid python.
        @type  filename: C{str}
        """
        LOGGER.debug("Reading %s", filename)
        settings_raw = {}
        execfile(filename, settings_raw)
        self.__dct.update(settings_raw)


def reload():
    global templates
    tpl_path = config.get("templates_file", "/etc/vigilo/vigirrd/templates.py")
    if not os.path.exists(tpl_path):
        LOGGER.warning("Can't find the template conf file: %s", tpl_path)
        templates = {}
        return
    current_timestamp = os.stat(tpl_path).st_mtime
    if tpl_path in MTIMES and current_timestamp <= MTIMES[tpl_path]:
        # non modifié
        LOGGER.debug("Not reading unchanged file %s", tpl_path)
        return
    settings.empty()
    settings.load_file(tpl_path)
    MTIMES[tpl_path] = current_timestamp
    templates = settings.get("templates", {})

# pylint: disable-msg=C0103
settings = Settings()
templates = {}
reload()


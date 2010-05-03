# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
################################################################################
#
# RRDGraph Python RRD Graphing library
# Copyright (C) 2007-2008 CS-SI
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
Configuration for RRDGraph basée sur des fichiers de conf.

Le fonctionnement est inspiré du module de configuration de Django.
"""

import sys
import glob
import os
import UserDict
from logging import getLogger
LOGGER = getLogger(__name__)

from tg import config

ALLOWED_KEYS = ("hostscfg", "templates", "labels")

__all__ = ("reload", "hosts", "templates", "labels")


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
        settings_raw = {}
        execfile(filename, settings_raw)
        self.__dct.update(settings_raw)

def reload():
    settings.empty()
    files = glob.glob(os.path.join(
                    config.get("conf_dir", "/etc/vigilo/vigirrd"), "*.py"))
    files.sort()
    for f in files:
        try:
            settings.load_file(f)
        except Exception, e:
            LOGGER.error("Error while parsing %s: %s\n" % (f, str(e)))
    del files

settings = Settings()
reload()
hosts = settings.get("hostscfg", {})
templates = settings.get("templates", {})
labels = settings.get("labels", {})


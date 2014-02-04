# -*- coding: utf-8 -*-
# Copyright (C) 2011-2014 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""WSGI environment setup for vigirrd."""

from vigirrd.config.app_cfg import base_config

__all__ = ['load_environment']

#Use base_config to setup the environment loader function
load_environment = base_config.make_load_environment()

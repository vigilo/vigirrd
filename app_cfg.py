# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2006-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Global configuration file for TG2-specific settings in vigirrd.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::

    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))

"""

import vigirrd, vigirrd.model
from vigilo.turbogears.configurator import Configurator
from os.path import dirname, abspath, join

options = {
    'static_labels': {
        'CAPTION': 'Value',
        'AVERAGE': 'avg',
        'MIN': 'min',
        'MAX': 'max',
        'LAST': 'last',
    },

    'model': vigirrd.model,
    'DBSession': vigirrd.model.DBSession,
    'paths': {
        'templates': [join(dirname(abspath(vigirrd.__file__)), 'templates')],
    },
}

# Create the final configuration for the application
base_config = Configurator('VigiRRD', vigirrd)
base_config.update_blueprint(options)

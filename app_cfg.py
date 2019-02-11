# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2006-2019 CS-SI
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

import os

from tg.configuration import AppConfig
from vigilo.turbogears import VigiloAppConfig

import vigirrd
import vigirrd.model
from vigirrd.lib import app_globals # pylint: disable-msg=W0611
# W0611: Unused import: imports nécessaires pour le fonctionnement

# Monkey-patch de la fonction dst() pour se conformer
# à l'API de datetime.tzinfo.utcoffset().
# Cf. https://bugs.launchpad.net/pytz/+bug/612081 pour plus d'information.
import pytz
pytz._FixedOffset.dst = lambda self, dt: pytz.ZERO

# Monkey-patch de la fonction dst() pour se conformer
# à l'API de datetime.tzinfo.utcoffset().
# Cf. https://bugs.launchpad.net/pytz/+bug/612081 pour plus d'information.
import pytz
pytz._FixedOffset.dst = lambda self, dt: pytz.ZERO


class VigiRRDConfig(VigiloAppConfig):
    def __init__(self, *args, **kwargs):
        super(VigiRRDConfig, self).__init__(*args, **kwargs)
        self.use_sqlalchemy = True
        self.model = vigirrd.model
        self.DBSession = vigirrd.model.DBSession

    def setup_paths(self):
        """
        Surcharge pour ne pas utiliser le système de thèmes de Vigilo.
        """
        super(VigiRRDConfig, self).setup_paths()
        root = os.path.dirname(os.path.abspath(self.package.__file__))
        self.paths["templates"] = [ os.path.join(root, "templates") ]

    def setup_sqlalchemy(self):
        # On revient au comportement par défaut de TG
        AppConfig.setup_sqlalchemy(self)

base_config = VigiRRDConfig('VigiRRD')
base_config.package = vigirrd

base_config.mimetype_lookup = {
    '.png':'image/png',
    '.csv': 'text/csv',
}

base_config.static_labels = {
    'CAPTION': 'Value',
    'AVERAGE': 'avg',
    'MIN': 'min',
    'MAX': 'max',
    'LAST': 'last',
}

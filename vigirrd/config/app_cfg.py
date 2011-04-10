# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
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
from vigirrd.lib import app_globals, helpers # pylint: disable-msg=W0611


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

base_config = VigiRRDConfig('vigirrd')
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


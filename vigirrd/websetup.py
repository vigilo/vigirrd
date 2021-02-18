# -*- coding: utf-8 -*-
# Copyright (C) 2011-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Setup the vigirrd application"""

from __future__ import print_function
import imp
import logging

import transaction
from tg import config

__all__ = ['setup_app']

log = logging.getLogger(__name__)

def setup_app(command, conf, variables):
    """Place any commands to setup vigirrd here"""
    # Charge le fichier "app_cfg.py" se trouvant aux côtés de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ conf.global_conf['here'] ])
    app_cfg = imp.load_module('vigirrd.config.app_cfg', *mod_info)

    # Initialisation de l'environnement d'exécution.
    base_config = app_cfg.base_config
    base_config.make_wsgi_app(conf.global_conf, conf.local_conf, wrap_app=None)

    # Load the models
    from vigirrd import model
    print("Creating tables")
    model.metadata.create_all(bind=config['tg.app_globals'].sa_engine)
    transaction.commit()
    print("Successfully setup")

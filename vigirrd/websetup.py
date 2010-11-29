# -*- coding: utf-8 -*-
"""Setup the vigirrd application"""

import logging

import transaction
from tg import config

from vigirrd.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)

def setup_app(command, conf, variables):
    """Place any commands to setup vigirrd here"""
    load_environment(conf.global_conf, conf.local_conf)

    # VigiRRD n'utilise pas la base de données.
    # Inutile de faire appel à vigilo.turbogears ou vigilo.models donc.

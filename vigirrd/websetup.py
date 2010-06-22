# -*- coding: utf-8 -*-
"""Setup the vigirrd application"""

import logging

import transaction
from tg import config

from vigirrd.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)

def setup_app(command, conf, variables):
    """Place any commands to setup vigiboard here"""
    from vigilo.turbogears import populate_db
    from vigiboard.config.environment import load_environment

    load_environment(conf.global_conf, conf.local_conf)
    populate_db()


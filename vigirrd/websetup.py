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

    # Load the models
    from vigirrd import model
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)
    transaction.commit()
    print "Successfully setup"

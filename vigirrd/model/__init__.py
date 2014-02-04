# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103
# Copyright (C) 2006-2014 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""The application's model objects""" 

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
DeclarativeBase = declarative_base()

# There are two convenient ways for you to spare some typing.
# You can have a query property on all your model classes by doing this:
# DeclarativeBase.query = DBSession.query_property()
# Or you can use a session-aware mapper as it was used in TurboGears 1:
# DeclarativeBase = declarative_base(mapper=DBSession.mapper)

# Global metadata.
# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata


def init_model(engine):
    """Call me before using any of the tables or classes in the model."""

    DBSession.configure(bind=engine)

# Import your model modules here.

from vigirrd.model.host import Host
from vigirrd.model.graph import Graph
from vigirrd.model.perfdatasource import PerfDataSource
from vigirrd.model.cdef import Cdef

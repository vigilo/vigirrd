# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# pylint: disable-msg=R0903,W0232
# Copyright (C) 2006-2014 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Perfdatasources: les indicateurs de métrologie"""

from sqlalchemy import Column
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, UnicodeText, Float

from vigirrd.model import DeclarativeBase, DBSession
from vigirrd.model.secondary_tables import GRAPH_PERFDATASOURCE_TABLE


class PerfDataSource(DeclarativeBase):
    """
    Une source de données de performance
    """
    __tablename__ = 'perfdatasource'

    idperfdatasource = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(UnicodeText, index=True, nullable=False)
    label = Column(UnicodeText, nullable=True)
    factor = Column(Float(precision=None, asdecimal=False),
                    default=1.0, nullable=False)
    max = Column(Float(precision=None, asdecimal=False))

    graphs = relation('Graph', secondary=GRAPH_PERFDATASOURCE_TABLE,
                         back_populates='perfdatasources', lazy=True)

    def __unicode__(self):
        return self.name
    def __str__(self):
        return str(self.name)

    @classmethod
    def by_name(cls, name):
        return DBSession.query(cls).filter(cls.name == unicode(name)).first()


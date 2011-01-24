# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Perfdatasources: les indicateurs de métrologie"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, Unicode, UnicodeText, Float

from vigirrd.model import DeclarativeBase, DBSession
from vigirrd.model.secondary_tables import GRAPH_PERFDATASOURCE_TABLE


class PerfDataSource(DeclarativeBase):
    __tablename__ = 'perfdatasource'
    
    idperfdatasource = Column(Integer, primary_key=True, autoincrement=True)
    #idgraph = Column(Integer, 
    #                 ForeignKey(Graph.idgraph),
    #                 autoincrement=True)
    #graph = relation('Graph', back_populates="perfdatasources", lazy=True)
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
